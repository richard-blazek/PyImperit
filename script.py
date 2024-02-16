import flask, file_load, route, new_game, os, random, time, data, action, json

lands=file_load.FileLoader('./static/lands.txt', scope={'Land': data.Land, 'Lands': data.Lands}).value
settings=file_load.FileLoader('./static/settings.txt', scope={'Settings': data.Settings}).value

flatten = lambda l: [item for sublist in l for item in sublist]

def get_mountains(lands):
	return flatten(flatten((([list(x) for x in land.border_with(land2)] for j,land2 in enumerate(lands) if i!=j and i not in land2.neighbors and not land.sea and not land2.sea) for i,land in enumerate(lands))))

def pt_eq(pt, p2):
	return int(round(pt[0]*1000))==int(round(p2[0]*1000)) and int(round(pt[1]*1000))==int(round(p2[1]*1000))

f=open('./Mountains.txt', mode='w', encoding="UTF-8")


pairs=get_mountains(lands)
mountains=[pairs[0]]
for pair in pairs:
	print(pair)
	cont=next((mt for mt in mountains if pt_eq(mt[-1], pair[0]) or pt_eq(mt[-1], pair[1]) or pt_eq(mt[0], pair[0]) or pt_eq(mt[0], pair[1])), None)
	if not cont:
		mountains.append(pair)
	else:
		at_end=pt_eq(cont[-1], pair[0])
		at_begin=pt_eq(cont[0], pair[0])
		at_end_rev=pt_eq(cont[-1], pair[1])
		at_begin_rev=pt_eq(cont[0], pair[1])
		if at_end:
			cont.append(pair[1])
		elif at_begin:
			cont.insert(0, pair[1])
		elif at_end_rev:
			cont.append(pair[0])
		elif at_begin_rev:
			cont.insert(0, pair[0])

for mountain in mountains:
	f.write(json.dumps({"Line":[{"x":point[0], "y":point[1]} for point in mountain]}, separators=(',', ':'))+'\n')
			

f.close()