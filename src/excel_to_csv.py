# #importing pandas as pd 
# import pandas as pd 

# # Read and store content 
# # of an excel file 
# read_file = pd.read_excel ("/Users/max/Desktop/extracted_funding_agencies.xlsx") 

# # Write the dataframe object 
# # into csv file 
# read_file.to_csv ("/Users/max/Desktop/extracted_funding_agencies.csv", 
# 				index = None, 
# 				header=True) 

def return_fibo_until_n(n: int) -> int:
		
		if n > 1:
			x, i = 0, 1
			result: list[int] = [0, 1]

			while len(result) <= n:
				sum = x + i
				result.append(sum)
				x, i = i, sum

			return result
		
		return 0

if __name__ == "__main__":
	fibo = return_fibo_until_n(2)
	print(fibo)