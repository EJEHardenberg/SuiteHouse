

#Creates a general knapsack that handles baseItems


# // Input:
# // Values (stored in array v)
# // Weights (stored in array w)
# // Number of distinct items (n)
# // Knapsack capacity (W)
# for w from 0 to W do
#   m[0, w] := 0
# end for 
# for i from 1 to n do
#   for j from 0 to W do
#     if j >= w[i] then
#       m[i, j] := max(m[i-1, j], m[i-1, j-w[i]] + v[i])
#     else
#       m[i, j] := m[i-1, j]
#     end if
#   end for
# end fong

import logging

class Knapsack:
	"""0-1 Knapsack """
	values = []
	limit = 0

	def __init__(self, limit=0,items=[]):
		#Round all values up and place into the values
		#also map each object
		self.values = []
		self.limit = 0
		for item in items:
			#need positive integers
			item.amount = round(abs(item.amount)+.5)
			self.values.append(item)

		self.limit = int(limit)


	def solve(self):
		#Construct a two dimensional array
		m = []
		for w in range(0,len(self.values)):
			inner = []
			for w in range(0,self.limit+1):
				inner.append(0)
			m.append(inner)
		for i in range(0,len(self.values)):
			for j in range(0,self.limit+1):
				if j >= int(self.values[i].amount):
					m[i][j] = max(m[i-1][j],self.values[i].amount + m[i-1][int(j-self.values[i].amount)])
				else:
					m[i][j] = m[i-1][j]
		#We now we know that m[n-1][W] is the maximum 'value' which is how much we actually filled the knapsack
		

		#We need to know which items were selected as well
		currentW = len(m[0])-1
		marked = []
		for i in range(0,len(self.values)):
			marked.append(0)



		#If cell[i,j] == cel[i-1,k] then item is not in the bag
		i = len(self.values)-1
		while(i >= 0 and currentW >= 0):
			if (i==0 and m[i][currentW] > 0) or (m[i][currentW] != m[i-1][currentW]):
				marked[i] = 1
				currentW = currentW - int(self.values[i].amount)
			i = i-1
		#marked now corresponds to which items are marked which we can use to sort which items were used or unused
		used = []
		unused = []
		value = 0
		
		for i in range(0,len(self.values)):
			if(marked[i] == 1):
				value += self.values[i].amount
				used.append(self.values[i].getJSON())
			else:
				unused.append(self.values[i].getJSON()) 

		#Return the total amount used, as well as the two lists of items generated
		return {'used' : value, 'usedItems' : used, 'unusedItems' : unused}














		
		