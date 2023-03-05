def partition(a, b, n):
	start = a
	inc = (b-a) // n

	l = []

	for i in range(n-1):
		l.append((start, start + inc))
		start += inc

	l.append((start, b))

	return l