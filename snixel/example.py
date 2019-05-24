from snixel import Snixel

snixel = Snixel()

func = snixel.addFunction("My Random Function")
# Add an input
func.addFunctionInput("random_val", "float", "Random Value")

# Get the input value. Possible values for type: float, float2, float3 and float4
node = func.addGetFloat("random_val", "float")

# Add a random node, to get any value between 0 and input
out = func.addRandom(node, "float")

# Set the output node
func.setOutput(out)

# Compile the output to file "random.sbs"
snixel.compile("random.sbs")
