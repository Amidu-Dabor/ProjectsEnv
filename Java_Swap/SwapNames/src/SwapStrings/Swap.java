package SwapStrings;
import java.util.*;

public class Swap {
	
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		SwapConfig swapObj = new SwapConfig();
		
		try (// Check for error & print output
		Scanner inputObj = new Scanner(System.in)) {
			System.out.println("Enter your first name: ");
			String fName = inputObj.nextLine();
			System.out.println("Enter your last name: ");
			String lName = inputObj.nextLine();
				
			System.out.println("\n");
				
			System.out.println("---------- NAMES BEFORE SWAPPING ----------");
			swapObj.setNames(fName, lName);
		}
		swapObj.getNames();
			
		System.out.println("---------- NAMES AFTER SWAPPING ----------");
		swapObj.swapNames();
		
	}

}
