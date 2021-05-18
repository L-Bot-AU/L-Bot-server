#include <iostream>
#include <fstream>
#include "include\nlohmann\json.hpp"
#include <string>
#include <iomanip>

using json = nlohmann::json;
using namespace std;

float take_valid_float(string input_request){
    bool valid = false;
    float input;
    do{
        cout << input_request;
        cin >> input;
        
        if(cin.good()){
            valid = true;
        } else{
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(),'\n');
            cout << "Invalid input; please re-enter.\n";
        }
    } while (!valid);
    return input;
}



int take_valid_integer(string input_request){
    bool valid = false;
    int input;
    do{
        cout << input_request;
        cin >> input;
        
        if(cin.good()){
            valid = true;
        } else{
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(),'\n');
            cout << "Invalid input; please re-enter.\n";
        }
    } while (!valid);
    return input;
}

int main(){
    const string location = "calcData.json";
    const string days[5] = {"Mon", "Tue", "Wed", "Thu", "Fri"};
    ifstream fin{location};
    
    string library;
    int year, b;
    float m;
    json data;
    fin >> data;
    char choice ='y';
    while(choice == 'y'){
        library = "";
        cout << "Enter Library Jnr/Snr: ";
        cin >> library;
        while (library!="Jnr" && library!="Snr"){
            cout << "Invalid input please retner library (Jnr/Snr): ";
            cin >> library;
            library[0] = toupper(library[0]);
            library[1] = tolower(library[1]);
            library[2] = tolower(library[2]);
        }
        
        bool valid = false;
        do{
            cout << "Enter year: ";
            cin >> year;
            
            if(cin.good()){
                if(year > 2010){
                    valid = true;
                } else {
                    cout << "Value entered for year too low re-enter.\n";
                }
            } else{
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(),'\n');
                cout << "Invalid input; please re-enter.\n";
            }
        } while (!valid);

        for(int i = 1; i<5; i++){ /*For the 4 terms*/
            for(int j=0; j<5; j++){ /*Each day of week*/
                cout << "For term " << i << " " << days[j] << " enter the following values for:";
                cout << "\n\tbefore school:\n";
                m = take_valid_float("\tGradient (m): ");
                b = take_valid_integer("\tConstant (b): ");
                data[library][to_string(year)]["Term"+to_string(i)][days[j]]["bs"]["m"] = m;
                data[library][to_string(year)]["Term"+to_string(i)][days[j]]["bs"]["b"] = b;
                
                cout << "\n\tbreak 1:\n";
                m = take_valid_float("\tGradient (m): ");
                b = take_valid_integer("\tConstant (b): ");
                data[library][to_string(year)]["Term"+to_string(i)][days[j]]["b1"]["m"] = m;
                data[library][to_string(year)]["Term"+to_string(i)][days[j]]["b1"]["b"] = b;
                
                cout << "\n\tbreak 2:\n";
                m = take_valid_float("\tGradient (m): ");
                b = take_valid_integer("\tConstant (b): ");

                data[library][to_string(year)]["Term"+to_string(i)][days[j]]["b2"]["m"] = m;
                data[library][to_string(year)]["Term"+to_string(i)][days[j]]["b2"]["b"] = b;
            }
        }
        ofstream fout{location};
        fout << setw(4) << data;
        cout << "Data saved, continue to add more data (y/n): ";
        cin >> choice;
    }
}