package SwapStrings;

public class SwapConfig {

	// Declaration of variables
	String firstName, lastName, names;

	// Set names
	public void setNames(String firstName, String lastName) {
		this.firstName = firstName;
		this.lastName = lastName;
	}
	
	// Get names and print before swapping
	public void getNames() {
		System.out.println(this.firstName + " " + this.lastName);
	}
	
	// Swap names
	public void swapNames() {	
		// Append last name to first name
		this.names = this.firstName + this.lastName;
		// Save first name in last name variable
		this.lastName = this.names.substring(0, this.names.length() - this.lastName.length());
		// Save last name in first name variable
		this.firstName = this.names.substring(this.lastName.length());
		
		// Print out names after swapping
		System.out.println(this.firstName + " " + this.lastName);
	}
	
}
