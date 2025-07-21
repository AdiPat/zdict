#!/bin/bash
# Script to tag the v1.0.0 release

echo "Creating v1.0.0 release tag..."

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0

## Features
- Initial release of zdict with five performance modes.
- Complete dict-compatible API implementation.
- C extension for high-performance operations.
- Pure Python fallback for environments without C compiler.
- Comprehensive test suite with 96% coverage.
- Performance benchmarking suite.
- Full type annotations for modern Python development.

## Performance Modes
- mutable: Standard dictionary with balanced performance.
- immutable: Frozen, hashable dictionary for use as keys.
- readonly: Optimized for maximum lookup performance.
- insert: Append-only dictionary for log-like workloads.
- arena: Pre-allocated dictionary with stable memory layout."

echo "Tag created successfully!"
echo ""
echo "To push the tag to remote:"
echo "  git push origin v1.0.0"
echo ""
echo "To push all tags:"
echo "  git push --tags"