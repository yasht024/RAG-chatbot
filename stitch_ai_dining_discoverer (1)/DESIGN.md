---
name: Fiscal Precision
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#3c4a43'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#6b7b72'
  outline-variant: '#bacac1'
  surface-tint: '#006c4f'
  primary: '#006c4f'
  on-primary: '#ffffff'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#2fe0aa'
  secondary: '#486081'
  on-secondary: '#ffffff'
  secondary-container: '#c0d9ff'
  on-secondary-container: '#465f80'
  tertiary: '#855300'
  on-tertiary: '#ffffff'
  tertiary-container: '#fda417'
  on-tertiary-container: '#673f00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#d3e3ff'
  secondary-fixed-dim: '#afc8ee'
  on-secondary-fixed: '#001c39'
  on-secondary-fixed-variant: '#2f4868'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 24px
  margin: 24px
  max-width: 1280px
---

## Brand & Style
The design system is engineered to evoke trust, security, and forward-looking financial growth. It targets sophisticated investors who value clarity and precision in their financial data. 

The aesthetic is a hybrid of **Minimalism** and **Glassmorphism**, emphasizing high-contrast readability and structural order. By utilizing significant whitespace and a refined color palette, the UI feels breathable yet authoritative. Transparency and blur effects are reserved for interactive layers to suggest depth and digital sophistication without compromising the professional, secure nature of a mutual fund assistant.

## Colors
The palette leverages high-contrast pairings to ensure WCAG accessibility.
- **Primary (Growth Teal):** Used for primary actions, success states, and growth indicators.
- **Secondary (Professional Navy):** Used for headers, prominent text, and brand grounding elements.
- **Accent (Warning Amber):** Reserved for ambiguity, alerts, or financial cautions.
- **Surface Strategy:** 
  - **Light Mode:** Uses `white` for base surfaces and `zinc-50` for secondary containers to maintain a sterile, professional look.
  - **Dark Mode:** Utilizes `slate-950` as the foundation with slightly lighter slate tones for layered surfaces to provide depth.

## Typography
The system uses a dual-font strategy to balance character with utility. 
- **Outfit** provides a modern, geometric friendliness to headlines, making large financial figures and section headers feel approachable.
- **Inter** is the workhorse for body text and data-heavy tables, chosen for its exceptional legibility and neutral tone. 
- **Hierarchy Note:** All labels and data captions use high-contrast Inter with increased letter spacing for immediate scanning.

## Layout & Spacing
The layout follows a **Fluid Grid** model with fixed maximum widths for desktop to ensure data density remains readable.
- **Rhythm:** A 4px base unit governs all dimensions.
- **Desktop:** 12-column grid with 24px gutters.
- **Mobile:** 4-column grid with 16px margins.
- **Logic:** Spacing between related items (like a label and an input) should use `sm` (8px), while spacing between sections should use `xl` (40px) to maintain a minimalist feel.

## Elevation & Depth
This design system uses a combination of **Tonal Layers** and **Glassmorphism**.
- **Base Level (0):** The main background (`white` or `slate-950`).
- **Surface Level (1):** Cards and main containers use a subtle 1px border (`slate-200` in light / `slate-800` in dark).
- **Interactive Level (2):** Chat bubbles and floating menus utilize a backdrop blur (12px) and 60% opacity of the surface color to create a "glass" effect, suggesting the assistant is an overlay on top of the financial data.
- **Shadows:** Use extremely soft, large-radius shadows (0 10px 30px rgba(0,0,0,0.05)) for floating elements to keep the UI light and modern.

## Shapes
A "Rounded" strategy is applied consistently to bridge the gap between technical precision and user friendliness.
- **Standard UI (Cards, Inputs):** 8px-12px corner radius.
- **Pill Shapes:** Full rounding is used exclusively for chips, tags, and main CTA buttons to make them feel tactile and distinct from structural containers.

## Components
- **Chat Bubbles:** Assistant responses use a glassmorphic Navy Blue background with White text (Dark Mode) or White background with Navy text (Light Mode). User bubbles use a subtle Zinc-100 fill.
- **Pill-Shaped Chips:** High-contrast backgrounds for active states (Teal for growth, Navy for generic filters). 
- **Input Fields:** Sleek, low-profile inputs with a 1px border. On focus, the border transitions to a 2px Teal outline with a subtle outer glow.
- **Buttons:**
    - *Primary:* Solid Teal background with White/Navy text, pill-shaped.
    - *Secondary:* Ghost style with 1px Navy or White border.
- **Cards:** White or Slate-900 backgrounds with 12px rounded corners and a subtle border rather than a heavy shadow.
- **Refusal States:** Components indicating a "No" or "Refusal" leverage the Amber-50 background with Amber-700 text to soften the impact while remaining clearly a warning.