import simplejson as json

txt = ""

name = input("Enter name: ").lower().replace(" ", "")
context = input("Enter context for conversation: ")
txt += context + "\n\n"

while True:
    print("Press enter and submit a blank line to end.")
    q = input("Q: ")
    if not q:
        break
    a = input("A: ")
    if not a:
        break
    txt += f"Q: \"{q}\"\nA: \"{a}\"\n"

print("Compiling...")
print(txt)
open(f"{name}.json", "w+").write(json.dumps({"name": name, "training_data": txt}, indent=2))
print("Compiled.")
input()