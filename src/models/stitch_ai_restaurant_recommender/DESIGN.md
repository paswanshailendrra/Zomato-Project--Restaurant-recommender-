---
name: Aetheris Antigravity
colors:
  surface: '#121414'
  surface-dim: '#121414'
  surface-bright: '#383939'
  surface-container-lowest: '#0d0e0f'
  surface-container-low: '#1a1c1c'
  surface-container: '#1e2020'
  surface-container-high: '#292a2a'
  surface-container-highest: '#343535'
  on-surface: '#e3e2e2'
  on-surface-variant: '#bbc9cf'
  inverse-surface: '#e3e2e2'
  inverse-on-surface: '#2f3131'
  outline: '#859399'
  outline-variant: '#3c494e'
  surface-tint: '#47d6ff'
  primary: '#a5e7ff'
  on-primary: '#003543'
  primary-container: '#00d2ff'
  on-primary-container: '#00566a'
  inverse-primary: '#00677f'
  secondary: '#edb1ff'
  on-secondary: '#520070'
  secondary-container: '#6e208c'
  on-secondary-container: '#e498ff'
  tertiary: '#dfdcdb'
  on-tertiary: '#313030'
  tertiary-container: '#c3c0c0'
  on-tertiary-container: '#4f4e4e'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#b6ebff'
  primary-fixed-dim: '#47d6ff'
  on-primary-fixed: '#001f28'
  on-primary-fixed-variant: '#004e60'
  secondary-fixed: '#f9d8ff'
  secondary-fixed-dim: '#edb1ff'
  on-secondary-fixed: '#320046'
  on-secondary-fixed-variant: '#6e208c'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c9c6c5'
  on-tertiary-fixed: '#1c1b1b'
  on-tertiary-fixed-variant: '#474646'
  background: '#121414'
  on-background: '#e3e2e2'
  surface-variant: '#343535'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-sm:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style
The design system embodies a premium, high-tech "Antigravity" aesthetic, moving away from traditional terrestrial UI toward a weightless, celestial experience. The target audience consists of power users and tech enthusiasts who value precision and futuristic elegance.

The visual style is a fusion of **Glassmorphism** and **High-Contrast Dark Mode**. It leverages depth through translucency rather than heavy shadows, creating an interface that feels like it is floating in deep space. Surfaces are defined by their refractive properties and thin, glowing boundaries, evoking a sense of advanced engineering and digital clarity.

## Colors
The palette is rooted in the void, using deep charcoal and pure black to provide infinite depth. 

- **Backgrounds:** Pure black (#000000) for the deepest layer, moving to deep charcoal (#0a0a0a) for container surfaces.
- **Accents:** Electric Blue (#00d2ff) serves as the primary action color, signifying energy and connectivity. Neon Purple (#9d50bb) is used for secondary actions, accents, and complex AI-driven states.
- **Typography:** Off-white (#f0f0f0) ensures maximum readability against dark backgrounds, while light gray (#a0a0a0) is reserved for secondary metadata and disabled states.
- **Gradients:** Use linear gradients transitioning from Electric Blue to Neon Purple at a 135-degree angle for primary "hero" elements.

## Typography
The system utilizes **Outfit** for the majority of the interface to maintain a modern, clean, and approachable geometric feel. Weight is used strategically to create hierarchy without needing excessive color variation.

For technical data, AI-generated explanations, and system-level logs, **JetBrains Mono** (a high-performance alternative to Roboto Mono) is used to reinforce the "high-tech" narrative. All labels should be set in monospace to provide a structured, engineered appearance.

## Layout & Spacing
The layout follows a fluid-to-fixed model. On desktop, content is housed within a 1280px central container using a 12-column grid. On mobile, the system shifts to a 4-column grid with reduced margins.

Spacing is strictly derived from an 8px linear scale. Large-scale sections should use generous padding (64px+) to simulate the "weightlessness" of the design, ensuring that elements never feel cramped or grounded by gravity.

## Elevation & Depth
Elevation is achieved through **Glassmorphism** and light-based layering rather than traditional drop shadows.

- **Surface Layer:** 40% opacity charcoal with a 12px backdrop blur.
- **Floating Layer:** 60% opacity with a 20px backdrop blur and a 1px inner border (stroke) using a low-opacity white (10%) to catch the "light."
- **Glow:** High-priority elements use a subtle outer glow (0px 0px 15px) utilizing the primary electric blue at 20% opacity to simulate light emission.

## Shapes
The shape language is "Sleek Aerodynamic." While the design is high-tech, it avoids harsh 0px corners to maintain a premium feel. 

Standard components use a 0.5rem (8px) radius. Larger containers and cards use a 1.5rem (24px) radius to emphasize the "capsule" or "cockpit" feel of the interface. Interactive elements like buttons should never be fully sharp.

## Components
- **Buttons:** Primary buttons use the Electric Blue to Neon Purple gradient with white text. On hover, the glow intensity increases. Secondary buttons use a transparent background with a 1px glowing Electric Blue border.
- **Inputs:** Fields are dark charcoal with a 1px border. On focus, the border transitions to Electric Blue and the background blur increases.
- **Cards:** Use the glassmorphic style described in Elevation. Cards should have a subtle 1px top-border gradient to simulate an overhead light source.
- **Chips:** Monospace text in small capsules with high-contrast backgrounds (Neon Purple at 15% opacity).
- **Progress Bars:** Thin, glowing lines using the primary gradient, featuring a trailing blur effect to simulate motion.
- **Status Indicators:** Use pulsing micro-animations for "Active" or "Processing" states to reinforce the high-tech, living nature of the system.