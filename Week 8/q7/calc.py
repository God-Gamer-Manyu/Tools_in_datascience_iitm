import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the employee data
df = pd.read_csv("./Week 8/q7/synthetic_employees.csv")   # Change path if needed

# 2. Calculate frequency count for the "Operations" department
operations_count = (df["department"] == "Operations").sum()

# 3. Print the frequency count to the console
print("Number of employees in Operations department:", operations_count)

# 4. Create a histogram (count plot) showing distribution of departments
plt.figure(figsize=(10, 6))
df["department"].value_counts().plot(kind="bar")

plt.title("Department Distribution")
plt.xlabel("Department")
plt.ylabel("Frequency")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("./Week 8/q7/department_distribution.png")  # Save the plot as an image file