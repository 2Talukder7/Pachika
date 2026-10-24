import json

with open("backend/data/recipes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Checking timings across all 31 recipes:")
for r in data["recipes"]:
    prep = r["prep_time_min"]
    cook = r["cook_time_min"]
    tot = r["total_time_min"]
    step_sum = sum(s.get("duration_min", 0) for s in r.get("steps", []))
    
    issues = []
    if prep + cook != tot:
        issues.append(f"prep({prep}) + cook({cook}) != tot({tot})")
    if step_sum != tot:
        issues.append(f"step_sum({step_sum}) != tot({tot})")
    if issues:
        print(f"[{r['id']}] {' | '.join(issues)}")
