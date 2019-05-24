# Snixel

Snixel is akin to a linker for the Snix programming language and is responsible
for keeping track of the nodes to be created, how they are linked together and
finally writing them to disk using the SBS Writer module.

If you don't like Snix's syntax and want to write a language of your own, you
can interface with Snixel. You can also use it to write your own functions
directly if you prefer that.

Here's how you would add a function, create a function input, get the value,
connect the value with a Random node and set it as the output node.

from snixel import Snixel

snixel = Snixel()

func = snixel.addFunction("My Random Function")

# Add a float input with the variable name "random_val" and a label of "Random Value"
func.addFunctionInput("random_val", "float", "Random Value")

# Get the input value. Possible type values: float, float2, float3 and float4
node = func.addGetFloat("random_val", "float")

# Add a random node, to get any value between 0 and input
out = func.addRandom(node, "float")

# Set the output node
func.setOutput(out)

# Compile the output to file "random.sbs"
snixel.compile("random.sbs")
