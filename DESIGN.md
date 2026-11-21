# DevPath Design System

> Definitive visual and interaction guidance for DevPath. The supplied hero reference is the primary source of truth; apply its indigo–purple world, bright yellow accents, bold type, and developer-focused code motif throughout the product. The additional supplied “How DevPath Works” screenshot is a secondary page reference for hierarchy and card spacing; its white treatment should not override the primary brand palette.

## 1. Overview and design philosophy

DevPath helps developers turn their skills and interests into meaningful software projects. The interface should feel **confident, creative, intelligent, approachable, and built for developers**—not like a generic admin template. Pair expressive indigo/purple canvases and yellow calls to action with calm, readable surfaces for dense content.

### Principles

1. **One recognizable brand:** indigo, purple, and DevPath yellow are present on every route, including authenticated and utility pages.
2. **Purposeful contrast:** use a rich hero gradient for brand moments; use lighter or dark elevated surfaces for long-form project content as appropriate, while retaining branded navigation, accents, and focus treatments.
3. **Content first:** give project titles, learning steps, and recommendations clear hierarchy and generous line spacing.
4. **Developer-native detail:** use monospace for code and technical metadata only; don’t turn the whole interface into a terminal aesthetic.
5. **Progress over decoration:** cards, badges, and progress visualization should explain the next useful action.
6. **Accessible by default:** never trade readable contrast, keyboard operation, or reduced-motion support for visual effects.

## 2. Brand identity

- **Name:** DevPath (render the wordmark as `Dev` in white/primary text and `Path` in yellow on dark branded surfaces; on light surfaces use deep indigo for `Dev` and indigo/purple or yellow for `Path` only where contrast permits).
- **Product:** an open-source skill-to-project recommender with roadmaps, starter code, and progress tools.
- **Personality:** bold, intelligent, modern, developer-focused, confident, approachable, creative, professional, tech-oriented.
- **Signature composition:** deep indigo navigation; indigo-to-violet hero; white headline with a yellow phrase; lavender supporting copy; yellow primary action; compact feature badge; dark code window; light floating feature cards.

Do not introduce unrelated brand colors, gradients, illustration styles, or component radii page by page.

## 3. Visual reference analysis

### Primary hero reference

The desktop composition is a dark indigo navigation bar above a wide two-column hero. The left column contains an outlined open-source badge, oversized three-line heading (first line white, emphasized lines yellow), a three-line lavender description, and two large pill CTAs. The right column stacks a light “Starter Code Ready” card, a charcoal code editor, and a light roadmap card. A subtle dotted texture and broad blue-to-purple glow add depth without competing with text.

Approximate desktop proportions at the supplied 1892 × 859 screenshot: navigation about 80 px high; hero content is centered in a max-width region of roughly 1450 px; left/right columns are near 1:1 with a generous central gap. At 1408 × 676, preserve the same hierarchy while scaling type and spacing so the editor and CTAs remain in the first viewport where practical.

### Secondary “How DevPath Works” reference

The separate screenshot shows a light section with a centered eyebrow and headline followed by three outlined, softly shadowed step cards connected by arrows. Preserve its whitespace, restrained borders, centered hierarchy, and step numbering, but keep DevPath identity visible through indigo/purple headings, yellow or indigo highlights, and branded focus/action states. Do not interpret this screenshot as permission to make the whole site generic white SaaS.

### Reference color estimates

Values below are practical approximations from the supplied rendered reference, not claims of pixel-level sampling from a source file. Prefer these consistent tokens over scattered guesses; refine only after sampling a provided source asset directly.

| Role | Token | HEX | Use |
|---|---|---:|---|
| Primary deep indigo | `--dp-indigo-950` | `#10145F` | Navigation and darkest hero edge |
| Indigo | `--dp-indigo-900` | `#171D70` | Brand background and dark surfaces |
| Blue-indigo | `--dp-indigo-800` | `#202B88` | Hero midtone |
| Purple | `--dp-purple-700` | `#4526A0` | Hero purple transition |
| Rich purple | `--dp-purple-600` | `#5525B5` | Hero bright edge / restrained accents |
| Yellow | `--dp-yellow-400` | `#FFC629` | Primary actions and key emphasis |
| Yellow hover | `--dp-yellow-500` | `#F5B814` | Hover/pressed primary action |
| Pale yellow | `--dp-yellow-100` | `#FFF4CC` | Soft highlight on dark surfaces |
| White | `--dp-white` | `#FFFFFF` | Inverse text and light surfaces |
| Off-white surface | `--dp-surface-light` | `#F7F6FB` | Floating cards and light cards |
| Lavender copy | `--dp-lavender-300` | `#B9B8D7` | Supporting text on dark brand backgrounds |
| Charcoal | `--dp-charcoal-950` | `#0D1117` | Code editor body |
| Charcoal header | `--dp-charcoal-900` | `#161B22` | Code editor title bar |
| Body text | `--dp-ink-900` | `#101828` | Text on light surfaces |
| Muted body | `--dp-ink-600` | `#526078` | Secondary copy on light surfaces |
| Border | `--dp-border-light` | `#E1E5EF` | Light-surface dividers |
| Success | `--dp-green-500` | `#19B981` | Status indicators (not decorative) |
| Error | `--dp-red-500` | `#EF5B5B` | Error feedback and editor control dot |
| Info | `--dp-blue-500` | `#4863F5` | Informational icons and links when appropriate |

### Semantic color tokens

Use semantic variables in component styles rather than literals. Each theme must preserve role and contrast.

```css
:root {
  --brand-primary: var(--dp-indigo-900);
  --brand-secondary: var(--dp-purple-700);
  --brand-action: var(--dp-yellow-400);
  --brand-action-hover: var(--dp-yellow-500);

  --bg-page: #f7f8fc;
  --bg-section: #eef1ff;
  --bg-surface: #ffffff;
  --bg-surface-raised: #ffffff;
  --bg-brand: var(--dp-indigo-950);
  --text-primary: var(--dp-ink-900);
  --text-secondary: var(--dp-ink-600);
  --text-inverse: #ffffff;
  --text-on-brand: #ffffff;
  --text-on-brand-muted: var(--dp-lavender-300);
  --border-default: var(--dp-border-light);
  --border-brand: rgb(255 255 255 / 18%);
  --focus-ring: var(--dp-yellow-400);
  --status-success: var(--dp-green-500);
  --status-warning: #D99500;
  --status-error: var(--dp-red-500);
  --status-info: var(--dp-blue-500);

  --hero-gradient: linear-gradient(112deg, #151b70 0%, #252184 53%, #5525b5 100%);
  --hero-glow: radial-gradient(ellipse at 86% 30%, rgb(115 62 220 / 42%), transparent 48%);
  --surface-gradient: linear-gradient(145deg, #fff 0%, #f6f5fb 100%);
  --code-bg: var(--dp-charcoal-950);
  --code-header-bg: var(--dp-charcoal-900);
}

html[data-theme="dark"] {
  --bg-page: #0b1027;
  --bg-section: #101735;
  --bg-surface: #151d3c;
  --bg-surface-raised: #1a2346;
  --text-primary: #f5f6ff;
  --text-secondary: #bdc4df;
  --border-default: #303b69;
  /* Keep yellow and indigo identity; do not turn all dark pages into gray. */
}
```

For RGB/alpha variants, use modern `rgb(r g b / alpha)` syntax where project browser support allows. Do not lower text opacity until contrast is checked. Yellow is best for dark backgrounds; on light surfaces use deep indigo text on yellow buttons. Avoid yellow for small text on white.

### Contrast and theme rules

- Meet WCAG 2.2 AA: at least 4.5:1 for normal text and 3:1 for large text and essential UI boundaries.
- Use white on deep indigo/purple; yellow headline emphasis is large and bold. Verify contrast for each gradient position, not only the start color.
- Use deep indigo text on yellow actions. Do not use pale lavender for small text on light backgrounds.
- Status must not be conveyed by color alone; pair with an icon/label or explicit text.
- Existing code has multiple token layers (`design-system.css`, `style.css`, `landing.css`) with inconsistent blue/default-light and purple landing values. New work should follow this document’s semantic token layer and avoid adding further one-off colors. Consolidate legacy tokens deliberately when modifying styles; don’t make broad visual changes as part of an unrelated task.

## 4. Typography

The current Flask templates load **Sora**, **Inter**, and **JetBrains Mono** from Google Fonts. Keep this stack; it already matches the reference and the app. Use no more than these two UI families plus the technical mono face.

| Role | Family | Weight | Desktop size / line height | Notes |
|---|---|---:|---|---|
| Display / hero H1 | Sora | 800 | clamp(3rem, 5vw, 5rem) / 1.05–1.1 | Tight tracking (-0.035em); allow intentional line breaks |
| Page H1 | Sora | 700–800 | 2.5–3.25rem / 1.1 | One clear page title |
| H2 | Sora | 700 | 2–2.5rem / 1.2 | Section title |
| H3 | Sora | 700 | 1.25–1.5rem / 1.3 | Card/title hierarchy |
| H4 | Sora | 600–700 | 1–1.125rem / 1.35 | Compact feature titles |
| Body | Inter | 400 | 1rem / 1.6–1.7 | Use 1.125rem for hero lead |
| Small / metadata | Inter | 400–600 | 0.8125–0.9375rem / 1.45 | Maintain contrast |
| Eyebrow / badge | Inter | 600–700 | 0.75–0.875rem / 1.3 | Uppercase, 0.06–0.1em tracking |
| Button / nav | Inter | 600–700 | 0.9375–1rem / 1.2 | Avoid tiny text |
| Code | JetBrains Mono | 400–500 | 0.8125–0.9375rem / 1.7 | Horizontal scrolling on narrow screens |

Fallbacks: `Sora, Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` for display; `Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` for body; `"JetBrains Mono", "SFMono-Regular", Consolas, monospace` for code. Prefer local/approved font hosting if deployment policy changes; do not add another font family without a clear need.

## 5. Spacing and layout

Use a 4 px base spacing unit. Existing stylesheet utilities include 4/8/12/16/24/32/48/64/96 px values; keep new work on this scale.

| Token | Value | Typical use |
|---|---:|---|
| `--space-1` | 4px | Icon/text gap, tight badge internals |
| `--space-2` | 8px | Compact control spacing |
| `--space-3` | 12px | Label/control spacing |
| `--space-4` | 16px | Standard component gap |
| `--space-6` | 24px | Card internals, grid gap |
| `--space-8` | 32px | Group spacing |
| `--space-12` | 48px | Section subgroups |
| `--space-16` | 64px | Compact section padding |
| `--space-20` | 80px | Standard desktop section padding |
| `--space-24` | 96px | Spacious desktop section padding |

- Main content max width: 1200–1280 px for standard pages; hero may extend to 1450 px at wide desktop to match reference proportions.
- Standard horizontal page gutter: 24 px desktop, 20 px tablet, 16 px mobile; never let content touch viewport edges.
- Long-form text measure: 65–78 characters per line. Hero description: max-width around 620 px.
- Cards: 24–32 px padding desktop, 20–24 px tablet, 16–20 px mobile.
- Section vertical rhythm: 80–96 px desktop, 64 px tablet, 48–56 px mobile. Use smaller spacing only for tightly related controls.

### Breakpoints

Match existing CSS breakpoints where possible (`640`, `768`, `992`, `1024` px), and avoid creating near-duplicate breakpoints.

| Range | Layout guidance |
|---|---|
| ≥1280 px desktop | Full composition, max-width container, two-column hero, 3–4 column grids |
| 1024–1279 px laptop | Narrower gutters, two-column layout with balanced columns, reduce oversized type |
| 768–1023 px tablet | Collapse hero to one column; center hero copy; product visual below; two-column grids |
| <768 px mobile | Compact nav/menu, one-column content, stacked forms and CTAs as needed; preserve readable type and touch targets |
| <400 px small mobile | Reduce heading and card padding; allow CTAs to wrap; prevent horizontal overflow |

Prefer Grid for true two-dimensional card layouts and Flexbox for nav bars, button groups, inline metadata, and component internals. Use normal flow; absolute positioning is reserved for hero decoration and the floating feature cards.

## 6. Gradients, borders, shadows, and radii

### Gradient and effects

- **Hero:** `linear-gradient(112deg, #151b70 0%, #252184 53%, #5525b5 100%)`, with a soft purple radial glow at the right; avoid harsh bands.
- **Background texture:** optional very subtle dots/grid at 4–8% opacity, decorative and hidden from assistive technology.
- **Surface:** white to pale lavender (`--surface-gradient`) only when it improves card separation.
- **Yellow action shadow:** `0 8px 24px rgb(255 198 41 / 24%)`; restrained, no permanent neon bloom.
- **Card shadow:** `0 8px 24px rgb(15 21 96 / 10%)`; elevate on hover by shadow and/or 2 px translation.
- **Focus:** 2 px solid yellow ring, 3 px offset on dark surfaces; on pale surfaces use deep indigo ring or yellow ring with a dark offset if needed to maintain visibility.
- Use borders (`rgb(255 255 255 / 16%)` on dark, `#E1E5EF` on light) rather than excessive glass effects.

### Radius scale

- Small chip/control: 8 px.
- Standard input/card: 12–16 px.
- Large feature/card surface: 20–24 px.
- Hero CTAs, nav GitHub control, status badges: fully rounded (`9999px`).
- Code panel: 16–20 px.

Keep radii consistent by component category. Do not mix unrelated sharp and pill styles within the same action group.

## 7. Component design system

All interactive components need visible hover, focus-visible, active/pressed, disabled, and (where relevant) loading states. Preserve native semantics. Minimum target size is 44 × 44 px for primary touch interactions (or sufficient spacing around smaller secondary icon controls).

### Navigation

**Landing navbar:** compact deep-indigo full-width band; content aligns to the hero container. Wordmark left; How It Works, Features, Find Project links and outlined GitHub action right. Reference links use soft lavender/white, with white hover and visible yellow focus. At mobile widths, replace crowded links with an accessible menu button and a properly labelled menu; don’t simply hide important navigation.

**Inner-page navbar:** use the same DevPath wordmark, typography, spacing, and signature accent. A light surface is acceptable for dense inner pages, but include an indigo/purple branded region or action accent so the page remains connected to the brand. Active route must be indicated by more than color alone (underline, weight, or `aria-current="page"`). Keep theme controls clearly labelled.

- Sticky nav, if used, must not obscure focus targets or anchor destinations.
- Use semantic `<nav aria-label="Primary">`, real links for navigation, buttons for actions, and a mobile menu button with `aria-expanded` and `aria-controls`.
- GitHub is an outlined pill on the dark nav; hover uses a subtle white surface. Do not make it look like the primary conversion action.

### Buttons

**Primary:** yellow fill, deep-indigo text, Sora/Inter semibold-bold, 16 px vertical / 28–36 px horizontal padding for hero CTAs, pill radius; slight lift and stronger shadow on hover; darker yellow on active. **Secondary:** transparent purple or translucent white fill on dark backgrounds, white text, thin border; on light surfaces use white/light-lavender fill with indigo text and border. **Outline:** transparent, clear border and label; hover fills subtly. **Ghost:** no permanent border, visible surface on hover. **Destructive:** semantic red with explicit label; never repurpose yellow. **Disabled:** muted color and no lift, maintain readable label, set `disabled`/`aria-disabled` correctly. **Loading:** retain button dimensions and label context, expose `aria-busy="true"`, avoid layout shift.

Buttons should have a 44 px minimum height, 8–16 px radius for standard controls and pill radius for hero/nav CTAs. Focus state must remain visible against both gradient and light surfaces. Avoid broad `transition: all`; animate only color, border, shadow, and transform.

### Cards and surfaces

- **Feature/floating hero cards:** near-white surface, deep ink title, muted slate description, 12–16 px radius, 20–24 px padding, small colored icon tile. The reference cards frame the code editor and should not overlap its readable content.
- **Project cards:** light or theme-appropriate surface, clear project title, skill/level badges, concise description, time/interest metadata, and one obvious action. Keep bookmarking and other secondary actions independently focusable.
- **Roadmap cards/steps:** ordered, numbered steps with clear completion status. Use yellow/indigo for progress; pair state icons with text. Keep step text and controls aligned.
- **Dashboard cards:** compact data surfaces with consistent padding, title, value, status, and optional trend/context. Charts use the brand palette plus accessible categorical colors, never color alone.
- **Information cards:** default border and subtle shadow; hover elevation only when clickable. A noninteractive card must not show pointer cursor or hover affordance.
- **Empty/error/loading states:** explain the situation and give one appropriate next action; use the same brand canvas and type scale.

### Forms and inputs

- Put a persistent visible label above each field; placeholder is supplementary, never the only label.
- Inputs/selects: full width, 44–48 px minimum height, 12 px radius, 12–16 px horizontal padding, semantic surface/text/border tokens.
- Focus: visible 2 px ring with offset; do not rely only on a subtle border color change.
- Validation: state the problem in text adjacent to the field; connect with `aria-describedby`, set `aria-invalid`, and preserve entered values where safe.
- Group radio/checkbox controls with `<fieldset>` and `<legend>`; provide an adequate clickable label area.
- Search fields should have a visible/accessible label, clear affordance, and clear results/empty/loading state.
- On mobile, fields stack; avoid cramped three-column forms.

### Badges, tabs, alerts, modals, toasts

- **Badges:** compact rounded pills with sufficient contrast; use indigo/lavender for neutral identity and semantic colors only for actual state. Keep text short.
- **Tabs:** semantic tab pattern with keyboard arrow navigation if implemented as tabs; active state uses an indicator and `aria-selected`, not color alone.
- **Alerts/toasts:** icon plus heading/body, semantic status, dismiss button with accessible name; do not convey urgency only through color. Toasts must not obscure primary controls.
- **Modals:** labelled dialog, focus trap, Escape handling where safe, initial focus, restore focus to trigger, scroll-contained content, close button at least 44 px. On mobile use near-full-screen layout and safe-area padding.
- **Tooltips:** supplementary, keyboard reachable, never the sole source of essential information.

### Tables, pagination, progress, data visualization

- Tables need visible headers, caption when useful, readable row spacing, and responsive horizontal scrolling or a well-designed stacked alternative on narrow screens.
- Pagination has labelled previous/next controls, current-page state, and disabled states.
- Progress bars need an accessible name and current/min/max values; complement with a percentage or step label.
- Use deep indigo, purple, yellow, and accessible secondary hues for charts. Keep gridlines muted; label important values directly; provide a text summary or data table when meaningful.

### Code and technical UI

The hero code panel is a charcoal rounded editor (`#0D1117`) with slightly lighter top bar (`#161B22`), three familiar status dots, filename in JetBrains Mono, and readable highlighted code. Code syntax colors: keyword coral (`#FF7B72`), function lavender (`#D2A8FF`), string pale blue (`#A5D6FF`), comment muted slate (`#8B949E`), default text near-white. Use semantic `<pre><code>` or equivalent and allow horizontal scroll on mobile; never shrink code below legibility just to fit.

## 8. Page-specific guidance

### Home / landing

Use the complete hero reference structure: badge, split-color headline, benefit description, primary and secondary CTAs, editor visual, and floating feature cards. Keep the page background/hero unmistakably indigo-purple. Below the hero, sections may introduce light surfaces for scanability, but preserve brand through section titles, small accents, primary actions, and shared nav/footer. The How It Works step cards should adopt the secondary reference’s spacing while using brand tokens.

### Explore Projects

Keep the global wordmark and navigation. Give search and filters a clear toolbar region; use a responsive project-card grid; make skill, level, and estimated-time metadata scannable. Use yellow for the main “find/continue” action, not every chip. Provide clear no-results and loading states.

### Compare Roadmaps

Use consistent project titles and badges above the comparison. Align roadmap phases in a readable grid on wide screens; on smaller screens stack or provide accessible horizontal scrolling. Distinguish differing steps through labels/icons in addition to color. Keep compare actions and selected projects visible.

### Project detail and roadmaps

Present title, level/interest/time badges, concise description, and primary action before long detail. Use timeline/ordered-list semantics for roadmap steps, accessible progress, resource links, and dark code panels with copy/download feedback. Maintain the same radii, focus ring, and typography.

### Dashboards, profile, progress

Use consistent page headings and card layouts; organize progress, saved items, certificates, and profile details into clear sections. Use purple/indigo for navigation and section emphasis, yellow for primary actions and progress highlights, neutral surfaces for dense data. Ensure chart/table content has text equivalents and meaningful labels.

### Authentication, forms, contact, admin

Use a restrained, focused branded composition—indigo/purple outer environment, readable light or dark form surface, yellow primary action, and familiar typography. Keep security/error messages explicit. Admin surfaces can be denser but must reuse the same component tokens and accessible focus/validation behavior.

### Footer

Use a deep-indigo or dark-purple surface, consistent wordmark, lavender links, clear headings, and yellow hover/focus accents. On small screens stack link groups with generous spacing; include meaningful focus indicators and avoid low-contrast copyright text.

## 9. Motion and interaction

- Standard transition: 160–220 ms ease-out for color, border, shadow, and small transform changes.
- Hover: subtle (1–2 px lift, modest shadow or surface shift); never move content enough to cause layout shift.
- Floating hero cards may drift gently by up to 8 px over 5–7 seconds. Avoid distracting animation and pause/disable under `prefers-reduced-motion: reduce`.
- Menu/modal transitions should be brief and preserve focus behavior. Loading uses a restrained spinner/skeleton with textual state where necessary.
- Avoid parallax, auto-playing motion, flashing, and blanket `transition: all`.
- Respect reduced motion in every animation and smooth-scroll behavior. Motion must never be needed to understand status.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 10. Responsive behavior

- **Desktop:** preserve the hero’s side-by-side text/visual layout; leave sufficient width for 3-line headline and code panel; align nav and hero to a common container.
- **Laptop:** reduce hero type and central gap before collapsing columns; keep feature-card edges inside the viewport.
- **Tablet:** stack hero content over product visual, center headline/CTA group where appropriate, and retain readable code width. Grid cards become two columns.
- **Mobile:** one-column flow; use a 2.25–3rem H1 depending on width; stack or wrap CTAs with equal-height targets; code panel may scroll horizontally; floating cards must not cover the heading or overflow viewport. Collapse grids and forms to one column.
- **Navigation:** accessible menu toggle on mobile; do not remove GitHub/project discovery links without an equivalent menu destination.
- **Tables:** scroll or transform to labelled cards; never clip columns silently.
- **Dialogs:** use full-width or near-full-screen content with safe-area padding; keep close and submit actions reachable.

Use `min()`, `max()`, and `clamp()` for fluid sizing where it reduces breakpoint churn. Test at 320 px, 375 px, 768 px, 1024 px, and 1440 px; check for horizontal overflow, overlap, clipped focus, and unreadable code.

## 11. Accessibility standards

- Use semantic landmarks (`header`, labelled `nav`, one main `h1`, `main`, sections with headings, `footer`) and logical heading order.
- Use keyboard-operable native links/buttons/inputs; keep tab order aligned with visual order; show `:focus-visible` clearly.
- Maintain WCAG 2.2 AA contrast for text and controls. Test gradient text at the least favorable position.
- Give informative images meaningful alt text; mark purely decorative background texture/icons `aria-hidden="true"`.
- Label form controls, associate errors/help text, announce async result/status changes with appropriate live regions, and avoid moving focus unexpectedly.
- Provide 44 × 44 px touch targets where possible and clear spacing between adjacent controls.
- Respect `prefers-reduced-motion`; do not use animation as the only status cue.
- Make focus visible in light and dark themes and ensure sticky headers do not obscure focused content.

## 12. Implementation standards for this repository

### Existing stack

DevPath is a **Flask/Jinja server-rendered application** with plain CSS and JavaScript, not a React/Next.js/Tailwind/shadcn app. Templates live in `src/templates/`; static assets and CSS live in `src/static/`. The shared base template loads `design-system.css` and `components.css`, and page-specific stylesheets are linked from each template. Google Fonts currently load Sora, Inter, and JetBrains Mono. Do not introduce a framework or build configuration for styling tasks.

### CSS conventions

- Prefer shared semantic variables and component classes; avoid new raw color literals outside token definitions.
- Scope page-specific rules under a page root class (`body.landing-page`, `.detail-page`, etc.) to prevent regressions.
- Use clear BEM-like names or existing class conventions (`.component`, `.component__part`, `.component--variant`) consistently.
- Prefer Flexbox for one-dimensional layout, Grid for card/comparison layouts, and avoid unnecessary absolute positioning.
- Keep selectors specific enough to avoid cross-page leakage, but avoid deeply nested selectors and `!important` except for a documented override.
- Use `:focus-visible`, not hover-only feedback. Define disabled/loading states alongside default styles.
- Avoid duplicate token sources. The current repository has competing token values across `design-system.css`, `style.css`, and `landing.css`; when performing a future CSS refactor, identify actual load order and consumers first, migrate one surface at a time, and remove a legacy token only after confirming there are no references.
- Use CSS custom properties for theme, spacing, radius, shadows, and typography. Page-level styles should consume semantic tokens rather than redeclare primitive palette values.
- Don’t change template/backend behavior just to apply visual styles. Keep HTML/Jinja semantic and accessible.

Example branded hero tokens for future CSS work:

```css
:root {
  --dp-indigo-950: #10145f;
  --dp-indigo-900: #171d70;
  --dp-purple-700: #4526a0;
  --dp-purple-600: #5525b5;
  --dp-yellow-400: #ffc629;
  --dp-lavender-300: #b9b8d7;
  --dp-charcoal-950: #0d1117;
  --font-display: "Sora", sans-serif;
  --font-body: "Inter", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
  --radius-card: 16px;
  --radius-pill: 9999px;
}

.hero {
  color: #fff;
  background: linear-gradient(112deg, #151b70 0%, #252184 53%, #5525b5 100%);
}
```

Do not paste this sample as a competing token block if equivalent semantic variables already exist; map current tokens to the documented values in a deliberate, tested refactor.

## 13. Do and don’t

### Do

- Keep indigo/purple and yellow visible on every major page.
- Use Sora for display/headings, Inter for UI/body, and JetBrains Mono only for code.
- Keep primary actions obvious, large enough, and high-contrast.
- Repeat consistent radii, spacing, borders, and focus states.
- Use the hero editor and floating feature-card pattern when it reinforces developer workflow.
- Preserve the secondary “How It Works” screenshot’s whitespace and legibility while carrying brand accents into it.
- Explain current design inconsistencies rather than silently spreading them.

### Don’t

- Replace the brand with generic blue, gray, or unrelated gradients.
- Make every card glassy, neon, or heavily shadowed.
- Use raw color values throughout page CSS or invent styles for each route.
- Use yellow body copy on white, low-contrast lavender on light backgrounds, or color-only status.
- Shrink code until it is unreadable or overlap floating cards with meaningful text.
- hide navigation links without an accessible mobile equivalent.
- Use hover as the only indication of interactivity.
- Treat the secondary white screenshot as the application-wide color direction.

## 14. Design consistency checklist

Before merging any UI change, verify:

- [ ] The page reads unmistakably as DevPath: indigo/purple identity, purposeful yellow accent, Sora/Inter typography.
- [ ] Colors map to semantic tokens; no arbitrary one-off palette was introduced.
- [ ] Content hierarchy, spacing, container width, card padding, and radius match the system.
- [ ] Primary, secondary, focus, hover, active, disabled, loading, empty, and error states are covered where relevant.
- [ ] Navigation, forms, cards, code, tables, and footer follow the shared patterns.
- [ ] Mobile layout preserves hierarchy and controls without overlap or horizontal overflow.
- [ ] Keyboard, screen-reader labels, focus visibility, contrast, and reduced motion were considered.
- [ ] New behavior is scoped to the intended page and does not regress another route or theme.
- [ ] The implementation fits the existing Flask/Jinja/plain-CSS/JavaScript stack.
