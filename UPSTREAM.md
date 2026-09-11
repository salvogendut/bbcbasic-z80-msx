<!-- SPDX-License-Identifier: BSD-3-Clause -->

# Upstream provenance

BBC BASIC for Z80 was originally written by R. T. Russell. Its original
project page is:

- `http://www.rtrussell.co.uk/bbcbasic/z80basic.html`

This MSX port is derived from the openly available BBC BASIC source subtree
in David Given's public CP/Mish repository:

- repository: `https://github.com/davidgiven/cpmish`
- source page: `https://github.com/davidgiven/cpmish/tree/master/third_party/bbcbasic`
- snapshot commit: `d70c643a5db24007ad6533f92b701fd714a99b7f`
- source directory: `third_party/bbcbasic`
- source tree object: `e9d0ae3c5f53fbd78379aa0d3f38d13f31c823f6`
- extracted branch: `upstream`
- extracted tip: `d4f2987a95f194a3431930340afbf1fc69f42125`
- immutable snapshot tag: `upstream-cpmish-d70c643`

The branch was produced from a full CP/Mish clone by selecting the 18 commits
which changed `third_party/bbcbasic`, preserving their authors, committers,
timestamps, messages, blobs, and order, and removing only the leading
directory from file paths. Git commit identifiers necessarily changed
because the tree paths changed.

The tree object at the extracted tip is exactly the same tree object as
`d70c643:third_party/bbcbasic`. A byte-for-byte directory comparison was also
performed before the MSX branch was created.

[docs/upstream-commit-map.tsv](docs/upstream-commit-map.tsv) records every
original CP/Mish commit and its extracted counterpart in chronological
order. Run `make verify-provenance` to validate the tag, tree, tip, and
extracted side of that map.

The `COPYING` file in the imported tree has SHA-256:

```text
cf5efb79a693ab044d2c5354d00f682e22fde66b428da1b4dc24cb1ad2ef42bb
```
