# Aceternity UI Design — Reference

## Architecture

Aceternity-style UI uses a layered composition approach:

```
Page
├── Background Layer (AnimatedGrid + Spotlight)
├── Content Layer
│   ├── Hero Section (Typewriter + GlowButton)
│   ├── Features Section (FeatureCard staggered grid)
│   ├── Stats Section (GlassCard + AnimatedCounter)
│   └── CTA Section (GlassCard with glow)
└── Navigation (sticky glassmorphism navbar)
```

## Component API

### AnimatedGrid
Interactive dot grid that pulses and responds to mouse proximity.
```
Props: { className?, dotSize?: number, spacing?: number, fade?: boolean }
```
- Draws dots on a `<canvas>` with mouse-reactive glow
- `spacing`: distance between dots (default 32px)
- `fade`: fade dots near edges for vignette effect
- Usage: absolute positioned behind content

### Spotlight
SVG blur filter that creates a soft glowing orb.
```
Props: { className?, fill?: string, size?: number }
```
- Creates a radial gradient with `feGaussianBlur`
- Uses CSS variable `var(--primary)` by default for theming
- Position absolute, z-index above background

### Typewriter
Cycling text with typing animation and blinking cursor.
```
Props: { texts: string[], speed?: number, deleteSpeed?: number, pauseDuration?: number }
```
- Alternates between texts array
- Types at `speed` ms/char, deletes at `deleteSpeed` ms/char
- Pauses `pauseDuration` ms at end of each text
- Includes animated `|` cursor

### GlowButton
Button with gradient shimmer, glow shadow, and scale interaction.
```
Props: { variant?: 'primary'|'outline', size?: 'sm'|'md'|'lg', loading?: boolean }
```
- `primary`: solid background with moving shimmer overlay on hover
- `outline`: border with glow shadow on hover
- Loading state shows spinner

### GlassCard
Glassmorphism container with backdrop blur, border, and optional glow.
```
Props: { hover?: boolean, glow?: boolean }
```
- Uses `backdrop-blur-xl` + semi-transparent gradient
- `hover`: lifts card on hover with deeper shadow
- `glow`: adds primary-colored glow shadow on hover
- Inner gradient overlay for depth

### FeatureCard
Animated card with staggered scroll reveal and hover glow.
```
Props: { icon: LucideIcon, title: string, description: string, index: number }
```
- `whileInView` with `delay: index * 0.1` for staggered reveal
- Radial gradient overlay on hover
- Icon container scales and glows on hover

### AnimatedCounter
Number that counts up from `from` to `to` when scrolled into view.
```
Props: { from?: number, to: number, duration?: number, suffix?: string, prefix?: string, decimals?: number }
```
- Uses IntersectionObserver to trigger animation once
- Cubic ease-out for smooth deceleration
- `decimals` for float values (e.g. 99.9)

## Animation Patterns

### Staggered Entry (list pages)
```tsx
const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }

<motion.div variants={container} initial="hidden" animate="show">
  {items.map(i => <motion.div key={i} variants={item}>...</motion.div>)}
</motion.div>
```

### Scroll Reveal (feature sections)
```tsx
<motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }} transition={{ duration: 0.7, delay: index * 0.1 }}>
  ...
</motion.div>
```

### Hover Scale (interactive cards)
```tsx
<motion.div whileHover={{ scale: 1.02, y: -2 }} transition={{ type: 'spring', stiffness: 300 }}>
```

### Page Layout Composition (landing)
```
<div className="min-h-screen overflow-hidden">
  <header className="fixed top-0 ... backdrop-blur-xl ...">  // sticky nav
  <section className="relative min-h-screen ...">
    <AnimatedGrid />
    <Spotlight className="-top-40 -left-40" />
    <motion.h1>...</motion.h1>    // animate in sequence
    <motion.p>...</motion.p>
    <GlowButton>...</GlowButton>
  </section>
  <section>
    <GlassCard>...</GlassCard>     // stats with AnimatedCounter
  </section>
  <section>
    <FeatureCard />               // staggered grid
  </section>
</div>
```

## Tailwind Configuration

Add CSS variables in `globals.css` for theme colors:
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --card: 0 0% 100%;
  --border: 214.3 31.8% 91.4%;
  --radius: 0.5rem;
}
```

Extend Tailwind config with `withOpacity` helper for CSS variable colors:
```js
function withOpacity(variable) {
  return ({ opacityValue }) =>
    opacityValue ? `hsla(var(${variable}), ${opacityValue})` : `hsl(var(${variable}))`
}
```
