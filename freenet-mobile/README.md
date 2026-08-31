# Freenet Mobile SDK

Freenet Mobile SDK is an iOS and Android library that puts the Freenet engine (freenet-core, the same code desktops run) inside a mobile app and connects it as a **thin peer**: a peer that uses the network without doing work for others.

This plan stands alone and nothing else requires it. A separate plan, [duty negotiation](../duty-negotiation/README.md), covers letting serving peers meter connections like these; this plan does not depend on it.

## 1. The thin peer

### 1.1 Why a phone can't do the usual work

A full peer does three jobs for other people, none optional:

- **Forwarding.** It passes other peers' messages toward their destination. Every connected peer is a candidate for this; there is no way to opt out.
- **Storing.** Data travels to its home address by hopping across peers, and each peer along the way keeps a copy and serves it to others from then on.
- **Broadcasting.** When a contract a peer follows changes, the peer re-sends the update to the other peers holding copies. This is the expensive one: during one incident ([#3791](https://github.com/freenet/freenet-core/issues/3791)), a gateway uploaded up to 163 bytes for every byte it downloaded.

On a phone, these jobs mean uploading for strangers all day: battery drain, data-plan drain, and exactly the background activity iOS and Android kill apps for.

### 1.2 What a thin peer is

A thin peer connects, reads and writes its own data, and follows its own contracts. It does none of 1.1's jobs:

- **Never selected.** The network never picks it to forward, store, or host anything.
- **Terminal delivery.** It receives the updates it subscribed to, and the chain stops there; it re-sends nothing.
- **Nothing unsolicited.** It is only ever sent what it asked for. Anything else is a protocol violation it rejects.

When the app is in the background, the phone is simply offline (2.3).

```
    peer ─── peer
    /           \
 peer           peer
    \           /   \
    peer ─── peer -- thin peer
       \     /
        \   /
      thin peer
```

### 1.3 Joining without duties

Joining is unchanged for everyone else. Thin is an exception the joiner asks for, with a new versioned CONNECT message naming the role. Gateways route the request to peers advertising room (1.4), and a serving peer with a free thin slot accepts. There is no credential, no payment, and no negotiation: a slot is free or it isn't.

Each serving peer sets its own cap on thin connections (operators can raise, lower, or zero it), and under pressure it sheds thin connections first. A shed or refused thin peer simply reconnects elsewhere. A gateway on an old version can't read the new CONNECT variant, so the thin peer fails closed and retries elsewhere rather than silently joining as a full peer.

One tradeoff is stated up front rather than hidden: the phone connects through a few serving peers, and those peers can see which contracts it reads, writes, and follows.

### 1.4 Extending freenet-core: generalize the transient path

The changes land in Core's shared connection modules, which is why any peer can request the role, not just mobile builds. Core is close to having this already: it has one connection type excluded from all three jobs, the **transient connection**, a short-lived slot a gateway opens for a peer that is still joining. The thin peer is that mechanism made a standing role.

| Property a thin edge needs | Where transient already provides it |
| --- | --- |
| A registry with a hard budget and race-safe accounting | `ConnectionManager::try_register_transient` / `drop_transient` / `transient_count` / `transient_budget` (`ring/connection_manager.rs:1741-1801`), including the undo-on-overshoot path |
| May carry no ring location | `try_register_transient(addr, location: Option<Location>)`; the location is already optional, so a location-less edge is not a new concept |
| Excluded from routing | `routing_candidates` skips transients (`connection_manager.rs:2515`) |
| Excluded from contract hosting | `k_closest_potentially_hosting` skips transients unconditionally, with no fallback (`ring.rs:3720`); exactly the semantic a thin edge wants, and deliberately stricter than the not-ready-peer filter beside it, which does fall back |
| Excluded from subscription-root selection | `ring.rs:1059`, whose comment records why: without it a peer whose only closer neighbour is transient fails to recognise itself as the terminus, wire-renews, dead-ends, and storms ([#4440](https://github.com/freenet/freenet-core/issues/4440)) |
| Regression protection for all three | Pin tests assert each selector still calls `is_transient(addr)` (`ring.rs:7091`, `:7142`), from [#4222](https://github.com/freenet/freenet-core/issues/4222) |
| A TTL and automatic reclamation | `transient_ttl`, with the lifecycle and its failure modes documented in [#4787](https://github.com/freenet/freenet-core/issues/4787) |

So "never selected" and "nothing unsolicited" (1.2) already exist. Three pieces are genuinely new:

1. **A standing slot instead of a countdown.** A transient slot expires after a fixed time and drops. A thin slot lives until either side disconnects or the serving peer sheds it, and it never converts into a ring connection.
2. **Terminal delivery (1.2).** Transient connections never subscribe, so nothing today delivers contract updates to one. It needs its own design and its own pin test (a test that fails if the guarantee is ever removed).
3. **Advertisement and a budget of its own.** Serving peers must be able to say "I accept thin peers" so gateways know where to route the request; the nearest existing shape is the readiness bit `routing_candidates` already checks over the wire (`connection_manager.rs:2526-2546`). And thin slots get their own counter and cap: the transient registry is already busy ([#4787](https://github.com/freenet/freenet-core/issues/4787) measured 368 transient expiries against 37 ring promotions in about 50 minutes on one gateway), and it was sized for 30-second joins, not connections that last as long as an app is open. The cleanup task must never reap a live thin connection as a stale joining slot.

## 2. Running applications on the phone

### 2.1 One engine: Core runs the contracts

_One platform difference: iOS forbids apps from generating machine code while running, so on iPhone the contract engine runs Wasmtime's interpreter backend, Pulley, instead of a just-in-time compiler. Same code, one configuration switch, somewhat slower execution._

```text
freenet-mobile/
  mobile-runtime/       Core embedding and lifecycle adapter
  mobile-storage/       platform paths, protection, migration
  native-api/           UniFFI interface for Swift and Kotlin
  ios/                  Swift application and platform integration
  android/              Kotlin application and platform integration
```

Bind the native API with UniFFI (a tool that generates Swift and Kotlin wrappers for Rust), with a small spike first to prove cancellation, streaming, and callback lifetimes map cleanly.

### 2.2 Native API

The `profile` argument carries the requested role (1.3) along with storage paths and network settings.

```text
start(profile) / stop() / status()

getContract(id)
putContract(contract, state)
updateContract(id, update)
subscribe(id) / unsubscribe(id)

registerDelegate(delegate)
sendDelegateMessage(delegate, message)

observeEvents()
```

### 2.3 Lifecycle

- **Foreground.** Open storage, restore the application list and pending requests, connect, let applications issue their normal reads and subscriptions, and resume pending writes only after fetching current state and revalidating.
- **Background.** Stop new work, cancel or finish the operations in flight, save state, disconnect, stop contract execution. Assume the OS grants no background time; every operation crossing the boundary must be safe to cancel and retry.
- **Offline writes.** Queue a write made offline only when the application's data rules support replaying it later. On reconnect, fetch current state, rebuild or revalidate the pending write, submit, and surface conflicts to the application. Merge rules make copies converge; they do not guarantee an old signed action is still valid.

### 2.4 Storage

Use Core's existing stores unless profiling finds a platform-specific problem. The categories need different protection because not everything is secret:

| Category | Protection |
| --- | --- |
| Public contract data the phone requested (code, parameters, public state) | Integrity checks |
| Data the application encrypted before writing it into a contract | The application's own encryption |
| Delegate secrets (the user's keys) | Encrypted delegate store, below |
| Mobile bookkeeping (pending operations) | Encrypted app storage |

The delegate store:

- A random encryption key protects it, and that key lives in the iOS Keychain or Android Keystore.
- No backup or sync: losing the phone loses the delegate secrets on it, unless an application provides its own recovery.

### 2.5 Contracts ship with the app and update over Freenet

Each app ships the contracts and delegates its features use (River, Marketplace, ...), and that set fixes what the app does. Freenet then keeps them current, delivering new revisions of those same contracts alongside their data. That respects the line Apple draws: downloaded code must not change an app's features, functionality, or primary purpose (App Store guideline 2.5.2 and the developer agreement's allowance for interpreted code); new features arrive through an app update and store review.

## 3. Delivery plan

### Phase 1: a real app on a normal peer, iOS and Android

Embed Core untouched and run one real application end to end on both platforms, joining the network as an ordinary peer.

- Embed Core (2.1), UniFFI spike first. Start in local mode (`OperationMode::Local`), which runs the whole engine with no network, so the app's shipped contracts and delegates (2.5) work before the first join; then switch the same instance to a normal network join.
- Build the lifecycle adapter (2.3) and the Keychain/Keystore-protected delegate store (2.4); test reinstall and OS upgrades.
- Measure everything: CPU, memory, bandwidth, battery, startup, shutdown, and specifically what the three jobs of 1.1 cost on cellular and on battery.

This phase is a test vehicle, not a shippable product; it runs on developer devices in the foreground. The measurements turn 1.1's argument into numbers for the maintainers, and they size Phase 2's default thin-slot cap.

### Phase 2: the thin role

Gated on maintainer approval; per CONTRIBUTING.md an approved design issue (RFC) is step zero.

- Land the CONNECT variant of 1.3 and the three work items of 1.4. Extend the pin tests so all three selectors provably skip thin edges, and add deterministic tests covering reconnects, shedding, timeouts, malformed messages, and downgrade attempts.
- Switch the Phase 1 app from an ordinary join to a thin request (one changed start profile, 1.3) and re-run the Phase 1 measurements.

At the end of this phase the product works: a real thin peer on iOS and Android.

## 4. Future improvement: a delegate trust anchor

A trust anchor would let one of the user's devices hold chosen delegate secrets for the others, which send it their signing and decryption requests. Either direction works: a desktop can anchor for a phone, or a phone for a desktop. Nothing in this plan needs it, so it is out of scope; every device runs its own instance holding its own secrets.

If it becomes worth building, the constraints are known:

- Opt-in and per delegate.
- Moves custody of a secret; never copies it.
- Requests are defined by the delegate and sit behind typed, revocable grants; no generic "sign anything" call.
- Its costs (a round trip to the other device, waiting when that device is unreachable, loss with that device) land wherever the user opts in.

Pairing, grant lifecycle, revocation, and enrolling a replacement device make it a plan of its own.

## 5. References

- Whitepaper vocabulary (peer, joiner, acceptance): [freenet/paper-1](https://github.com/freenet/paper-1), routing section
- Ring, hosting, and subscriptions: freenet-core `docs/architecture/ring/README.md`
- Operations (GET/PUT/UPDATE/SUBSCRIBE): freenet-core `docs/architecture/operations/README.md`
- Client API exposure and trust model: freenet-core `docs/client-api-exposure.md`
- Delegate secrets at rest: freenet-core `docs/secrets-at-rest.md`
- Demand-driven memory/storage discussion: freenet-core issue [#4651](https://github.com/freenet/freenet-core/issues/4651)
- Prior maintainer intent for embedded mobile nodes: discussions [#811](https://github.com/freenet/freenet-core/discussions/811) and [#420](https://github.com/freenet/freenet-core/discussions/420)
