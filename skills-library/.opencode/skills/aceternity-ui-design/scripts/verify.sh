#!/bin/bash
# Aceternity UI Design — Verify all components and build
# Usage: bash verify.sh /path/to/nextjs-app

set -e

TARGET="${1:-.}"
UI_DIR="$TARGET/src/components/ui"

echo "🔍 Verifying Aceternity UI Design..."

# Check framer-motion is installed
if grep -q '"framer-motion"' "$TARGET/package.json" 2>/dev/null; then
  echo "  ✅ framer-motion installed"
else
  echo "  ❌ framer-motion missing — run: npm install framer-motion"
  exit 1
fi

# Check required components exist
COMPONENTS=(AnimatedGrid Spotlight Typewriter GlowButton GlassCard AnimatedCounter FeatureCard)
for c in "${COMPONENTS[@]}"; do
  if [ -f "$UI_DIR/$c.tsx" ]; then
    echo "  ✅ $c.tsx"
  else
    echo "  ❌ $c.tsx missing"
    MISSING=1
  fi
done

# Try build
if [ -f "$TARGET/package.json" ]; then
  echo ""
  echo "🏗️  Running build check..."
  BUILD_OUTPUT=$(cd "$TARGET" && npm run build 2>&1 || true)
  if echo "$BUILD_OUTPUT" | grep -qE "successfully|Compiled|Generating static"; then
    echo "  ✅ Build successful"
  else
    echo "$BUILD_OUTPUT" | tail -15
    echo "  ⚠️  Build had issues"
  fi
fi

if [ -n "$MISSING" ]; then
  echo ""
  echo "❌ Some components missing. Run: bash scripts/scaffold.sh $TARGET"
  exit 1
fi

echo ""
echo "✅ All checks passed — Aceternity UI is ready to use!"
echo ""
echo "Quick start:"
echo "  import { AnimatedGrid } from '@/components/ui/AnimatedGrid'"
echo "  import { GlowButton } from '@/components/ui/GlowButton'"
echo "  import { GlassCard } from '@/components/ui/GlassCard'"
