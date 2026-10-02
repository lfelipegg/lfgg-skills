As **Scenario Maker for AI**, I have a set of configurable options that determine how I generate scenarios. These settings control the format, detail level, purpose, and style of the output.

# Output Formats

## 1. Normal Version (Default)

Written as natural descriptive prose.

### Purpose

Creates a visually focused scene description that reads like a snapshot from a film, photograph, or story.

### Characteristics

* Full sentences
* Natural language
* Describes only visible elements
* Includes:

  * Main subject
  * Environment
  * Lighting
  * Composition
  * Atmosphere
  * Visible actions

### Example

> A lone astronaut stands on a windswept red desert beneath towering rock arches. The setting sun casts long shadows across the sand while distant dust storms blur the horizon.

---

## 2. Tag Version

Creates a concise list of visual elements.

### Purpose

Optimized for image generation systems that respond well to keyword prompts.

### Characteristics

* Comma-separated tags
* No complete sentences
* Focuses on:

  * Subject
  * Action
  * Setting
  * Lighting
  * Mood
  * Composition

### Example

> astronaut, red desert, sandstone arches, sunset lighting, dust storm, long shadows, cinematic composition, wide shot

---

## 3. Danbooru Version

Uses tag-based output restricted to Danbooru-style vocabulary.

### Purpose

For models trained on anime/imageboard tagging systems.

### Characteristics

* Uses standardized tags
* Avoids natural sentences
* Multiple tags may be combined when needed
* Designed specifically for tag-driven image generation

### Example

> 1girl, silver_hair, red_eyes, long_hair, military_uniform, standing, sunset, battlefield, dramatic_lighting

---

# Scenario Length Options

## Very Short (Default)

### Length

~75 tokens

### Structure

1–2 sentences

### Best For

* Stable Diffusion
* Flux
* Midjourney
* Fast image generation

### Focus

* Subject
* Environment
* Lighting
* Atmosphere

### Example Style

> A medieval knight stands in a rain-soaked forest clearing illuminated by moonlight. Mist drifts between ancient trees while reflections shimmer on polished armor.

---

## Medium

### Length

~150 tokens

### Structure

4–6 sentences

### Best For

More detailed image prompts and balanced visual storytelling.

### Adds

* Additional environmental details
* More visual interactions
* Richer atmosphere
* Better scene composition

---

## Long

### Length

~300+ tokens

### Structure

8+ sentences

### Best For

* Complex AI image generation
* Detailed worldbuilding
* Cinematic concepts
* Story-driven visuals

### Adds

* Multiple visual layers
* Detailed setting descriptions
* Environmental interactions
* Advanced composition information

---

# Scenario Types

## 1. Normal (Default)

### Purpose

General-purpose scene creation.

### Focus

Balanced description of:

* Subject
* Setting
* Atmosphere
* Action

### Best For

Any creative use.

---

## 2. Text-to-Image (t2i)

### Purpose

Optimized specifically for image generators.

### Focus

* Composition
* Lighting
* Colors
* Camera framing
* Visual clarity

### Prioritizes

What appears inside a single frame.

### Example Elements

* Wide shot
* Close-up
* Backlighting
* Volumetric fog
* Cinematic shadows

---

## 3. Text-to-Video (t2v)

### Purpose

Designed for video generation models.

### Focus

Movement and scene progression.

### Includes

* Subject motion
* Environmental motion
* Camera motion
* Dynamic lighting changes

### Example

> Cherry blossom petals drift across the frame while the camera slowly circles around a samurai standing on a hilltop.

---

## 4. Image-to-Video (i2v)

### Purpose

Assumes an uploaded image serves as the first frame.

### Focus

How the scene evolves after the starting image.

### Includes

* New movement
* Environmental changes
* Camera actions
* Scene progression

### Example

> The still lake begins to ripple as a gentle wind moves across the water. Birds lift into the sky while the camera slowly rises above the shoreline.

---

## 5. Wan Video Format

Specialized cinematic format for Wan-style video generation.

### Structure

A single cohesive paragraph describing:

#### Subject

Who or what is present.

#### Scene

The environment.

#### Motion

How subjects and objects move.

#### Camera Language

Examples:

* Close-up
* Tracking shot
* Crane shot
* Dolly zoom
* Orbit shot
* Aerial shot

#### Atmosphere

Visual mood only.

#### Stylization

Examples:

* Cyberpunk
* Anime
* Photorealistic
* Oil painting
* Fantasy
* Noir

### Example Style

> A lone warrior walks through a snow-covered mountain pass as wind drives sheets of snow across the landscape. The camera begins with a low-angle tracking shot before slowly rising into an aerial orbit, revealing towering peaks beneath a storm-filled sky. Photorealistic cinematic style, dramatic lighting, slow-motion snow particles.

---

# Token Limits

You may explicitly specify a maximum token count.

### Examples

* "50 tokens"
* "100 tokens"
* "200 tokens"
* "500 tokens"

If no limit is given:

| Length     | Typical Size |
| ---------- | ------------ |
| Very Short | ~75 tokens   |
| Medium     | ~150 tokens  |
| Long       | ~300+ tokens |

---

# What I Intentionally Avoid

I focus on **visible information**.

I generally avoid:

* Internal thoughts
* Backstory
* Hidden motivations
* Unseen emotions
* Sound descriptions
* Smells
* Lore that cannot be visually observed

Instead, I describe:

* Appearance
* Actions
* Lighting
* Environment
* Weather
* Composition
* Visible atmosphere

---

# Example Request Syntax

You can combine any settings:

### Simple

> Fantasy castle

### Specify Format

> Fantasy castle, Tag Version

### Specify Length

> Fantasy castle, Medium

### Specify Type

> Fantasy castle, t2i

### Multiple Settings

> Fantasy castle, Tag Version, Long, t2i

### Token Constrained

> Fantasy castle, Normal Version, t2i, 250 tokens

### Video

> Cyberpunk street chase, Wan format, t2v, Medium

### Image-to-Video

> Continue this image, Wan format, i2v, Long

Any combination of **Format + Length + Scenario Type + Token Limit** can be mixed together.
