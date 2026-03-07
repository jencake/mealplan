# Mealplan CLI

Meal schedule CLI that displays daily meals with calendar conflict detection. Includes optional pregnancy tracking features.

## Installation

```bash
cd ~/code/mealplan
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Usage

### Show Schedule

```bash
# Today's schedule
mealplan today
mealplan show today

# Tomorrow's schedule
mealplan tomorrow

# Specific date
mealplan 2026-03-15

# Skip calendar conflict detection
mealplan today --no-calendar
```

### Log What You Ate

Record what was actually eaten (no AI needed):

```bash
# Log a meal
mealplan log breakfast "yogurt and berries"
mealplan log lunch "salad from Sweetgreen"
mealplan log dinner "pasta with marinara" --time 7:30pm

# Log time change for a meal, rest of the schedule will adjust accordingly
mealplan log afternoon-snack -t 4:00pm

# Log for a different date
mealplan log lunch "leftover pizza" --date yesterday
mealplan log breakfast "eggs and toast" --date 2026-03-01

# Log iron supplement (marks it as taken for alternation)
mealplan log iron "taken with orange juice"
```

**Valid meal names:**
- `breakfast`
- `morning-snack`
- `lunch`
- `afternoon-snack`
- `dinner`
- `evening-snack`
- `iron`

## Override Files

Overrides are stored at:
```
~/.config/mealplan/overrides/YYYY-MM-DD.md
```

Format (markdown table):
```markdown
| Meal | Time | Override |
|------|------|----------|
| Lunch | 1:00pm | Eating out at Local Deli |
| Dinner | 7:30pm | Date night at Italian restaurant |
```

- **Meal**: The meal name to override (Breakfast, Lunch, Dinner, etc.)
- **Time**: New time (leave empty to keep default)
- **Override**: New description/plan for that meal

To skip iron for a day, add `skip iron` or `no iron` anywhere in the override file.

---

## Configuration

Environment variables can be set in a `.env` file in the project root (auto-loaded at startup):

```bash
# ~/code/mealplan/.env
OUTLOOK_CALENDAR_ICS=https://outlook.office365.com/owa/calendar/...
MEALPLAN_PREGNANCY_ENABLED=true
MEALPLAN_PREGNANCY_DUE_DATE=2026-06-04
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MEALPLAN_WAKE_TIME` | No | `7:00am` | Your typical wake time |
| `OUTLOOK_CALENDAR_ICS` | No | - | Outlook calendar ICS URL for conflict detection |
| `MEALPLAN_PREGNANCY_ENABLED` | No | `false` | Enable pregnancy tracking (`true`, `1`, or `yes`) |
| `MEALPLAN_PREGNANCY_DUE_DATE` | No* | - | Due date in `YYYY-MM-DD` format (*required if pregnancy enabled) |

### Pregnancy Tracking (Optional)

Pregnancy features are **disabled by default**. To enable:

```bash
export MEALPLAN_PREGNANCY_ENABLED=true
export MEALPLAN_PREGNANCY_DUE_DATE=2026-06-04
```

When enabled, the schedule displays:
- Current pregnancy week
- Baby development milestones
- Trimester-specific nutrition tips

---

## Meal Schedule Reference

### Iron Supplement Schedule
- **Pattern**: Every other day (alternates automatically)
- **Timing**: Dynamically scheduled based on meal gaps
  - Non-workout days: 5:00pm standalone (2h after snack, 1h+ before dinner)
  - Workout days: With evening snack (iron-friendly: orange + berries)
- **Note**: Vitamin C aids absorption; avoid calcium within 2 hours

### Collagen Supplement
- **Workout days (Wed/Fri/Sun)**: In post-workout smoothie
- **Non-workout days (Mon/Tue/Thu/Sat)**: In matcha latte at 3:00pm

---

### Monday (Simple Prep)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 1 cup Greek yogurt + ½ cup berries + ¼ cup granola |
| 10:00am | Morning Snack | 1 apple + 2 tbsp Nutella |
| 12:30pm | Lunch | 1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast |
| 3:00pm | Afternoon Snack | ½ cup cottage cheese + ½ cup pineapple |
| 3:00pm | Matcha Latte | 1 cup oat milk + 1 tsp matcha + 1 scoop collagen |
| 6:30pm | Dinner | 1 cup tofu with sesame oil & soy sauce + 1 cup brown rice + 1 cup steamed cabbage |
| 8:30pm | Evening Snack | 1 banana + 10 almonds |
| 10:30pm | Bedtime | |

### Tuesday (Simple Prep)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 1 cup Greek yogurt + ½ cup berries + ¼ cup granola |
| 10:00am | Morning Snack | ¼ cup candied almonds |
| 12:30pm | Lunch | 1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast |
| 3:00pm | Afternoon Snack | 6 oz yogurt + 1 tbsp honey |
| 3:00pm | Matcha Latte | 1 cup oat milk + 1 tsp matcha + 1 scoop collagen |
| 5:30pm | Iron Supplement | 🩸 Take 1 hour before dinner |
| 6:30pm | Dinner | 1 cup tofu with sesame oil & soy sauce + 1 cup brown rice + 1 cup steamed carrots |
| 8:30pm | Evening Snack | 1 cup warm milk + 1 tsp honey |
| 10:30pm | Bedtime | |

### Wednesday (Simple Prep + Workout)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 1 cup Greek yogurt + ½ cup berries + ¼ cup granola |
| 10:00am | Morning Snack | 1 string cheese + ½ cup grapes |
| 12:30pm | Lunch | 1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast |
| 3:00pm | Afternoon Snack | ½ cup cottage cheese + ½ cup pineapple |
| 3:30pm | Pre-Workout | Pre-workout powder + water |
| 4:30pm | Workout | 30-minute workout |
| 5:00pm | Post-Workout Smoothie | Tropical Mango: 1 cup milk + 2 scoops protein + 1 cup mango + splash OJ + 1 scoop collagen |
| 6:30pm | Dinner | 1 cup tofu with sesame oil & soy sauce + 1 cup brown rice + 1 cup steamed cabbage |
| 8:30pm | Evening Snack | 1 banana + 10 almonds |
| 10:30pm | Bedtime | |

### Thursday (Simple Prep)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 1 cup Greek yogurt + ½ cup berries + ¼ cup granola |
| 10:00am | Morning Snack | ¼ cup candied walnuts |
| 12:30pm | Lunch | 1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast |
| 3:00pm | Afternoon Snack | 6 oz yogurt + 1 tbsp honey |
| 3:00pm | Matcha Latte | 1 cup oat milk + 1 tsp matcha + 1 scoop collagen |
| 5:30pm | Iron Supplement | 🩸 Take 1 hour before dinner |
| 6:30pm | Dinner | 1 cup tofu with sesame oil & soy sauce + 1 cup brown rice + 1 cup steamed carrots |
| 8:30pm | Evening Snack | 1 cup warm milk + 1 tsp honey |
| 10:30pm | Bedtime | |

### Friday (Indulgent + Workout)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 2 scrambled eggs + 1 slice whole wheat toast + ½ avocado + ½ orange |
| 10:00am | Morning Snack | ¼ cup candied cashews |
| 12:30pm | Lunch | Turkey sandwich: 3 oz turkey + ½ avocado ✓ + 2 slices whole wheat |
| 3:00pm | Afternoon Snack | Smoothie: 1 cup spinach + 1 banana + 1 cup milk |
| 3:30pm | Pre-Workout | Pre-workout powder + water |
| 4:30pm | Workout | 30-minute workout |
| 5:00pm | Post-Workout Smoothie | Strawberry Banana: 1 cup milk + 2 scoops protein + 1 cup strawberry banana + 1 scoop collagen |
| 6:30pm | Dinner | 4 oz roast chicken + 1 cup roasted potatoes + ½ orange ✓ |
| 8:30pm | Evening Snack | 1 banana + 10 almonds |
| 10:30pm | Bedtime | |

### Saturday (Indulgent)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 2 scrambled eggs + 1 slice whole wheat toast + ½ avocado + ½ orange |
| 10:00am | Morning Snack | 1 cheese stick + 6 crackers + ½ orange ✓ |
| 12:30pm | Lunch | Caesar salad: 2 cups romaine + 3 oz chicken + ½ avocado ✓ + 2 tbsp dressing |
| 3:00pm | Afternoon Snack | ¼ cup hummus + 1 cup veggie sticks |
| 3:00pm | Matcha Latte | 1 cup oat milk + 1 tsp matcha + 1 scoop collagen |
| 5:30pm | Iron Supplement | 🩸 Take 1 hour before dinner |
| 6:30pm | Dinner | 4 oz roast chicken + 1 cup roasted potatoes |
| 8:30pm | Evening Snack | 1 oz cheese + 6 crackers |
| 10:30pm | Bedtime | |

### Sunday (Indulgent + Workout)
| Time | Meal | Description |
|------|------|-------------|
| 7:30am | Breakfast | 2 scrambled eggs + 1 slice whole wheat toast + ½ avocado + ½ orange |
| 10:00am | Morning Snack | 1 apple + 2 tbsp Nutella |
| 12:30pm | Lunch | Turkey sandwich: 3 oz turkey + ½ avocado ✓ + 2 slices whole wheat |
| 3:00pm | Afternoon Snack | Smoothie: 1 cup spinach + 1 banana + 1 cup milk |
| 3:30pm | Pre-Workout | Pre-workout powder + water |
| 4:30pm | Workout | 30-minute workout |
| 5:00pm | Post-Workout Smoothie | Blueberry Vanilla: 1 cup milk + 2 scoops protein + 1 cup blueberry + 1 tsp honey + 1 scoop collagen |
| 6:30pm | Dinner | 4 oz roast chicken + 1 cup roasted potatoes |
| 8:30pm | Evening Snack | 1 cup warm milk + 1 tsp honey + ½ orange ✓ |
| 10:30pm | Bedtime | |

✓ = uses the other half from breakfast

---

## Trimester Guidelines

### 1st Trimester (Weeks 1-13)
- **Extra calories**: +0 (no increase needed)
- **Protein**: 60-75g daily
- **Focus**: Folate, managing nausea, small frequent meals
- **Tips**: Ginger for nausea, bland foods if queasy, prenatal vitamin timing

### 2nd Trimester (Weeks 14-27)
- **Extra calories**: +340/day
- **Protein**: 75-100g daily
- **Focus**: Iron absorption, energy maintenance, baby's rapid growth
- **Tips**: Pair iron with vitamin C, stay hydrated, calcium for bones

### 3rd Trimester (Weeks 28-40)
- **Extra calories**: +450/day
- **Protein**: 100g+ daily
- **Focus**: Smaller meals (less stomach room), calcium, preparing for labor
- **Tips**: Eat smaller portions more frequently, dates for labor prep, omega-3s for brain

---

## Weekly Development Milestones

| Week | Baby Size | Key Development |
|------|-----------|-----------------|
| 13-14 | Lemon | Fingerprints forming, can suck thumb |
| 15-16 | Apple | Hearing developing, can sense light |
| 17-18 | Pear | Fat layer forming, can yawn |
| 19-20 | Banana | Vernix coating, halfway point! |
| 21-22 | Papaya | Eyebrows visible, sleep cycles |
| 23-24 | Grapefruit | Lungs developing, responds to sounds |
| 25-26 | Cauliflower | Eyes open, brain rapid growth |
| 27-28 | Eggplant | Can dream, practices breathing |
| 29-30 | Butternut squash | Bones hardening, head-down position |
| 31-32 | Coconut | Fingernails complete, gaining ~0.5 lb/week |
| 33-34 | Pineapple | Immune system developing, less room to move |
| 35-36 | Honeydew | Lungs nearly mature, dropping into pelvis |
| 37-38 | Winter melon | Full term! Ready for birth |
| 39-40 | Watermelon | Fully developed, any day now! |
