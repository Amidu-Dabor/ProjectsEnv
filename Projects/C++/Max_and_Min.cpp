#include <iostream>
using namespace std;

class MaxMin{
	
	public: // Declaring a public scope to the functions of MaxMin class
		
		// Max function declaration
		int Max(){
			
			// Declaring array and initializing values
			int values[10] = {73, 2, 8, 5, 32, 44, 90, 82, 91, 50};
	
			int maximum = values[0];
	
			// Looping through to find maximum value
			for(int i = 1; i < 10; i++){
				if(values[i] > maximum){
					maximum = values[i];
				}
			}
	
			return maximum;
		}
		
		// Min function declaration
		int Min(){
			
			// Declaring array and initializing values
			int values[10] = {73, 2, 8, 5, 32, 44, 90, 82, 91, 50};
	
			int minimum = values[0];
	
			// Looping through to find minimum value
			for(int i = 1; i < 10; i++){
				if(values[i] < minimum){
					minimum = values[i];
				}
			}
	
			return minimum;
		}
	
};



int main(int argc, char** argv) {
	
	// Creating an instance of MaxMin class
	MaxMin maxminObj;
	
	cout << "\nFINDING MAXIMUM AND MINIMUM NUMBERS" << endl;
	
	cout << "--------------------------------------------------------\n" << endl;
	
	// Output
	cout << "MAXIMUM VALUE IS " << maxminObj.Max() << ".\n" << endl;

	cout << "MINIMIM VALUE IS " << maxminObj.Min() << "." << endl;
		
	return 0;
		
};
