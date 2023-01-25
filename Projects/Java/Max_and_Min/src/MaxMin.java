
public class MaxMin {
	
	//Max function declaration
	public int Max() {
		
		// Declaring array and initialising values
		int values[] = {73, 2, 8, 5, 32, 44, 90, 82, 91, 50};
		
		int maximum = values[0];
		
		// Looping through to find maximum value
		for(int i = 1; i < values.length; i++){
			
			if(values[i] > maximum){
				
				maximum = values[i];
				
			}
		}
		
		// Output
		return maximum;
		
	}
	
	// Min function declaration
	public int Min(){
				
		// Declaring array and initializing values
		int values[] = {73, 2, 8, 5, 32, 44, 90, 82, 91, 50};
		
		int minimum = values[0];
		
		// Looping through to find minimum value
		for(int i = 1; i < values.length; i++){
			if(values[i] < minimum){
				minimum = values[i];
			}
		}
		
		// Output
		return minimum;
	}

}
