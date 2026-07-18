---
name: aceternity-ui-design
description: Build Aceternity-style animated UI with framer-motion + Tailwind
---

# Aceternity UI Design Skill

## When to Use
- Building animated, premium-looking React/Next.js interfaces
- Need Aceternity-style components (spotlight, glassmorphism, typewriter, animated grids)
- Want scroll-triggered animations, hover effects, and micro-interactions

## Instructions
1. Install framer-motion: `npm install framer-motion`
2. Run scaffold script: `bash ./scripts/scaffold.sh <project-dir>`
3. Import components from `@/components/ui/` in your pages
4. Wrap page sections with `motion.div` + stagger containers
5. Use `AnimatedGrid` + `Spotlight` as page background layers

## Validation
- [ ] Components compile without TypeScript errors
- [ ] Animations trigger on scroll (whileInView)
- [ ] Hover effects work (scale, glow, gradient shift)
- [ ] GlassCard renders with backdrop-blur
- [ ] AnimatedGrid responds to mouse movement
- [ ] Build passes with `npm run build`

See [REFERENCE.md](./REFERENCE.md) for component API and animation patterns.
