"""
ID: your_id_here
LANG: PYTHON3
TASK: milk2
"""
fin = open('milk2.in', 'r')
fout = open('milk2.out', 'w')

n = int(fin.readline().strip())
intervals = []
for _ in range(n):
    s, e = map(int, fin.readline().split())
    intervals.append((s, e))

intervals.sort()

merged = []
cur_s, cur_e = intervals[0]
for s, e in intervals[1:]:
    if s <= cur_e:
        cur_e = max(cur_e, e)
    else:
        merged.append((cur_s, cur_e))
        cur_s, cur_e = s, e
merged.append((cur_s, cur_e))

longest_milk = max(e - s for s, e in merged)
longest_idle = 0
for i in range(1, len(merged)):
    gap = merged[i][0] - merged[i - 1][1]
    if gap > longest_idle:
        longest_idle = gap

fout.write(str(longest_milk) + ' ' + str(longest_idle) + '\n')
fout.close()
