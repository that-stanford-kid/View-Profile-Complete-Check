# min count algo
def minCount(comps):
	counts = [1 for n in comps]

for i in range(len(comps)-1):
	if comps[i]<counts[i+1]:
		counts[i+1] = counts[i]+1
for i in reversed(range(1, len(competitors))):
	if competitors[i-1]>counts[i]:
		counts[i-1] = max(counts[i]+1, counts[i-1])
return sum(counts)
