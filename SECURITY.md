# Security policy

## Supported versions

Only the latest release receives fixes, security fixes included. No release has been published yet.

| Version | Supported |
|---|---|
| latest release | yes |
| anything older | no |

## Reporting a vulnerability

Please report it privately through GitHub's private vulnerability reporting:
[open a draft security advisory](https://github.com/Deluha/icecrown/security/advisories/new). Do not
open a public issue, pull request or discussion.

Include what you found, how to reproduce it, the version and platform, and the impact you expect. You
will get an acknowledgement within seven days and a plan within thirty. The fix is released, and the
advisory published with credit to you if you wish, once a fixed version is available.

## Scope

In scope: anything in this repository and the published `icecrown` package — for example a way to
make the library execute code, write outside the snapshot store, or leak a connection string or cell
values into a baseline file, a log or an error message.

Out of scope, by design (see the [compatibility promise](docs/compatibility.md)): the fingerprint
detects accidental change and is not a defence against a deliberately constructed collision; its
hashes are unsalted, so a baseline of small or low-entropy data does not keep that data secret.
