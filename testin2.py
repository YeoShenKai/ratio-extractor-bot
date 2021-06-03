test = ['1','2.6','3', '-']
test2 = list(filter(lambda x: x != '-', test))
test3 = list(map(lambda x: float(x), test2))
test4 = sum(test3)
test5 = sum(list(map(lambda x: float(x), filter(lambda x: x!= '-', test))))
test6 = list(filter(lambda x: x.isnumeric(), test))
test7 = list(filter(lambda x: x.replace('.', '', 1).isdecimal(), test))