
from platform import node

def print_instructions_v2(results:dict):
    instructions = "EVACUATION ROUTE INSTRUCTIONS:\n"

    # destination
    instructions += f"Starting Location: {results['route'][0]}\nDestination: {results['route'][-1]}\n\n"

    # route
    instructions += "Location Path:\n\n"
    
    for i in range(len(results['route'])-1):

      # instructions += f" {i+1}. From {results['route'][i-1] if i > 0 else results['name']} proceed to {results['route'][i]}\n"
      instructions += f" {i+1}. {results['route'][i]} -> {results['route'][i+1]}\n"
    instructions += f"\nTotal Distance: {results['distance']} units\n"
    instructions += f"Estimated Time: {results['time']} hours\n"
    instructions += f"Destination Elevation: {results['desination_elevation']}\n\n"

    return instructions


def print_results(results):

  with open ("print_results.txt", "w") as file:
     file.write(results)

def main():

    input = {
        "name": "A",
        "distance": 5,
        "time": 10,
        "route": ["A", "j1", "c"],
        "desination_elevation": 4.5
    }
    result = print_instructions_v2(input)
    print(result)

    print_results(result)



if __name__ == "__main__":
    main()