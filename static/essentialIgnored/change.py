auto = []
with open("effectsNeeded.txt") as f:
    auto = f.readlines()

auto2 = []
for line in auto:
    auto2.append(line.replace("\n", ""))
print(auto2)

regLines = []
with open("effectsSolved.txt") as f:
    regLines = f.readlines()

first = []
i = 0
new = []
for line in regLines:
    if line.split("-")[0] in auto2:
        new.append(line)
    i+=1

with open('new.txt', 'w+') as f:
    for line in new:
        f.write("%s" % line)
    print('Done')





