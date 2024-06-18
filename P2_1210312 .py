#Hala Mohammed
#1210312
#Sec : 4
#*******************************************************************************************************************

import os #for operating system finctions
import subprocess #running external commands
import re  
import glob
import xml.etree.ElementTree as ET #for XML 

#*******************************************************************************************************************
# Define recommendations for each command
chmod_recommendations = ["id", "kill", "htop", "pmap", "rsync"]
uname_recommendations = ["ls", "ps", "top", "df", "dmesg"]
ps_recommendations = ["top", "htop", "pgrep", "killall", "pmap"]
top_recommendations = ["htop", "ps", "kill", "pgrep", "pmap"]
pkill_recommendations = ["kill", "killall", "ps", "top", "htop"]
cp_recommendations = ["rsync", "mv", "scp", "cpio", "cat"]
mv_recommendations = ["cp", "rsync", "rename", "cpio", "find"]
rm_recommendations = ["rmdir", "unlink", "mv", "find", "ls"]
touch_recommendations = ["echo", "printf", "cat", "date", "cp"]
whoami_recommendations = ["id", "logname", "users", "groups", "w"]
cat_recommendations = ["more", "less", "head", "tail", "nano"]
echo_recommendations = ["printf", "echo -e", "cat", "awk", "sed"]
free_recommendations = ["vmstat", "top", "htop", "cat /proc/meminfo", "pmap"]
date_recommendations = ["cal", "echo $(date +%Y-%m-%d)", "uptime", "clock", "hwclock"]
df_recommendations = ["du", "lsblk", "fdisk -l", "mount", "stat"]
du_recommendations = ["df", "ls", "find", "tree", "stat"]
hostname_recommendations = ["dnsdomainname", "domainname", "uname -n", "hostname -f", "host"]
pwd_recommendations = ["cd && pwd", "dirs -v", "pwd -P", "echo $PWD", "find pwd"]
grep_recommendations = ["ack", "egrep", "fgrep", "zgrep", "ripgrep"]
mkdir_recommendations = ["ls", "cd", "rm", "cp", "mv"]

#*******************************************************************************************************************
# Global variable to store command recommendations - Dictionary
command_recommendations = {}

#*******************************************************************************************************************

class CommandManualGenerator:
    
    # Constructor
    def __init__(self, commands_file_path="commands.txt"):
        self.commands_file_path = commands_file_path
        self.command_recommendations = {}
        self.last_search = None 
    #-----------------------------------------------------------------------------------------
    #Creates the 'CommandManuals' directory if it doesn't exist
    def create_manuals_directory(self):
        try:
            os.makedirs("CommandManuals", exist_ok=True) # If the directory already exists,os.makedirs will not raise an error. 
        except OSError as error:
            print(f"Error while creating directory for Manuals: {error}")
            exit(1)
    #-----------------------------------------------------------------------------------------
    #Reads commands from the file and returns a list
    def read_commands_from_file(self):
        if not os.path.exists(self.commands_file_path): # returns True if the path exists
            print(f"Error: File '{self.commands_file_path}' not found!")
            exit(1)

        with open(self.commands_file_path, "r") as commands_file:
            # Read the commands from the file , and return a list.
            return [command.strip() for command in commands_file]
    #-----------------------------------------------------------------------------------------
    # generates a manual for a given command 
    def generate_manual_for_command(self, command):
        description = self.get_command_description(command)
        if not description:
            print(f"Error: Failed to retrieve description for command {command}")
            return

        #the first five lines of the description
        first_five_lines = "\n".join(description.splitlines()[:5])
        version = subprocess.getoutput(f"{command} --version")
        example = self.get_command_example(command)

        try:
            execute_example = subprocess.run(example, shell=True, check=True, capture_output=True, text=True).stdout.strip()
        except subprocess.CalledProcessError as e:
            execute_example = f"Error executing example: {e}"

        related_commands = self.get_related_commands(command)
        self.command_recommendations[command] = related_commands

        self.write_manual(command, first_five_lines, version, example, execute_example, related_commands)
        print(f"Manual generated for {command}")
    #-----------------------------------------------------------------------------------------
    def get_command_description(self, command):
      description = subprocess.run(["man", command], capture_output=True, text=True).stdout.split("DESCRIPTION")[1].split("OPTIONS")[0]
      description = ' '.join(description.splitlines()[:5])

      
      example = self.get_command_example(command)
      version = subprocess.getoutput(f"{command} --version")
      related_commands = self.get_related_commands(command)
      
      #CommandManual object 
      command_manual = CommandManual(
        command,
        description,
        version,  
        example,  
        example,
        related_commands
      )
      
      #Serialize the CommandManual object to an XML string
      xml_string = XmlSerializer.serialize(command_manual)

      if "error" in description.lower():
         return None

      return description.strip()
    #-----------------------------------------------------------------------------------------    
    def get_command_example(self, command):
        # Dictionary of examples 
        examples = {
         "whreris": "whereis",
        "cp": "echo 'Hala Mohammed' > from && cp from to && ls && rm from",
        "mv": "echo 'Hala Mohammed' > from && mv from into && ls && rm into",
        "rm": "touch Thefile && ls && rm Thefile && ls",
        "free": "free",
        "ps": "ps",
        "top": "top -n 1 -b",
        "pkill": "echo 'Hi' > killfile; pkill -9 {command}; rm killfile",
        "echo": "echo 'Hala Mohammed'",
        "uname": "uname -a",
        "date": "date",
        "chmod": "touch TheEfile && chmod 755 TheEfile && ls && rm TheEfile && ls",
        "df": "df",
        "du": "du",
        "pwd": "pwd",
        "grep": "echo 'Hiiii' > ExampleFile && grep 'Hiiii' ExampleFile && rm ExampleFile",
        "touch": "touch newfile && ls && rm newfile && ls",
        "whoami": "whoami",
        "cat": "echo 'Hala Mohammed - 1210312' > File && cat File && rm File",
        }
        return examples.get(command, command)

    #-----------------------------------------------------------------------------------------
    def get_related_commands(self, command):
        try:
            result = subprocess.run(["bash", "-c", f"compgen -c | grep '{command}'"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting related commands: {e}")
            return None

    #-----------------------------------------------------------------------------------------
    def write_manual(self, command, description, version, example, execute_example, related_commands):
        # # Open a file in write mode
        with open(f"CommandManuals/{command}.xml", "w") as command_manual:
            command_manual.write(f'<Manuals>\n')
            command_manual.write(f'  <CommandManual>\n')
            command_manual.write(f'    <CommandName>{command}</CommandName>\n')
            command_manual.write(f'    <CommandDescription>{description}</CommandDescription>\n')
            command_manual.write(f'    <VersionHistory>{version}</VersionHistory>\n')
            command_manual.write(f'    <Example>{example}</Example>\n')
            command_manual.write(f'    <ExecuteExample>{execute_example}</ExecuteExample>\n')
            command_manual.write(f'    <RelatedCommands>{related_commands}</RelatedCommands>\n')
            command_manual.write(f'  </CommandManual>\n')
            command_manual.write(f'</Manuals>\n')

    #-----------------------------------------------------------------------------------------
    def generate_manuals(self):
        self.create_manuals_directory()
        commands = self.read_commands_from_file()
        for command in commands:
            self.generate_manual_for_command(command)
        print("All Manuals are generated!")

    #-----------------------------------------------------------------------------------------
    def verify_manual(self, command):
      # the path to the manual file for the given command
      CommandManual = f"CommandManuals/{command}.xml"

      if not os.path.exists(CommandManual):
        print(f"Error: The Manual for {CommandManual} does not exist.")
        exit(1)

      with open(CommandManual, "r") as manual_file:
        xml_content = manual_file.read()
 
      verification_failed = False  # Variable to track verification failure
      
      #/////////////////////////////////////////////////////////
      # Verify the CommandDescription section
      start_tag = "<CommandDescription>"
      end_tag = "</CommandDescription>"

      start_index = xml_content.find(start_tag)
      end_index = xml_content.find(end_tag)

      if start_index == -1 or end_index == -1 or end_index <= start_index:
        print(f"Error: Unable to find CommandDescription tags in {CommandManual}.")
        exit(1)

      ActualD = xml_content[start_index + len(start_tag):end_index].strip()

      
      close_tag_index = xml_content.find("</CommandDescription>", end_index)

      if close_tag_index == -1:
        print(f"Error: Unable to find the closing tag of CommandDescription in {CommandManual}.")
        exit(1)

      
      ExpectedD = self.get_command_description(command)

      if ExpectedD != ActualD:
        verification_failed = True
        print(f"Error: The Description is not verified for {command}!")
        print(f"Expected Description: {ExpectedD}")
        print(f"Actual Description:   {ActualD}")

      #/////////////////////////////////////////////////////////
      start_tag = "<ExecuteExample>"
      end_tag = "</ExecuteExample>"

      start_index = xml_content.find(start_tag)
      end_index = xml_content.find(end_tag)

      if start_index == -1 or end_index == -1 or end_index <= start_index:
        print(f"Error: Unable to find Example tags in {CommandManual}.")
        exit(1)

     
      ActualExample = xml_content[start_index + len(start_tag):end_index].strip()

     
      close_tag_index = xml_content.find(end_tag, end_index)

      if close_tag_index == -1:
        print(f"Error: Unable to find the closing tag of Example in {CommandManual}.")
        exit(1)

      
      ExpectedExample = subprocess.getoutput(self.get_command_example(command))

      if ExpectedExample != ActualExample:
        verification_failed = True
        print(f"Error: The Example is not verified for {command}!")
        print(f"Expected Example: {ExpectedExample}")
        print(f"Actual Example:   {ActualExample}")
      
      #/////////////////////////////////////////////////////////
      start_tag = "<VersionHistory>"
      end_tag = "</VersionHistory>"

      start_index = xml_content.find(start_tag)
      end_index = xml_content.find(end_tag)

      if start_index == -1 or end_index == -1 or end_index <= start_index:
        print(f"Error: Unable to find VersionHistory tags in {CommandManual}.")
        exit(1)

      
      ActualVersionHistory = xml_content[start_index + len(start_tag):end_index].strip()

    
      close_tag_index = xml_content.find(end_tag, end_index)

      if close_tag_index == -1:
        print(f"Error: Unable to find the closing tag of VersionHistory in {CommandManual}.")
        exit(1)

     
      ExpectedVersionHistory = subprocess.getoutput(f"{command} --version")

      if ExpectedVersionHistory != ActualVersionHistory:
        verification_failed = True
        print(f"Error: The VersionHistory is not verified for {command}!")
        print(f"Expected VersionHistory: {ExpectedVersionHistory}")
        print(f"Actual VersionHistory:   {ActualVersionHistory}")
      #/////////////////////////////////////////////////////////
      start_tag = "<RelatedCommands>"
      end_tag = "</RelatedCommands>"

      start_index = xml_content.find(start_tag)
      end_index = xml_content.find(end_tag)

      if start_index == -1 or end_index == -1 or end_index <= start_index:
        print(f"Error: Unable to find RelatedCommands tags in {CommandManual}.")
        exit(1)

      
      ActualRelatedCommands = xml_content[start_index + len(start_tag):end_index].strip()

     
      close_tag_index = xml_content.find(end_tag, end_index)

      if close_tag_index == -1:
        print(f"Error: Unable to find the closing tag of RelatedCommands in {CommandManual}.")
        exit(1)

    
      ExpectedRelatedCommands = self.get_related_commands(command)

      if ExpectedRelatedCommands != ActualRelatedCommands:
        verification_failed = True
        print(f"Error: The RelatedCommands are not verified for {command}!")
        print(f"Expected RelatedCommands: {ExpectedRelatedCommands}")
        print(f"Actual RelatedCommands:   {ActualRelatedCommands}")

      #/////////////////////////////////////////////////////////
      if not verification_failed:
        print(f"Verification successful for {command}")

    #-----------------------------------------------------------------------------------------
    def verify_manuals(self):
        commands = self.read_commands_from_file()
        for command in commands:
            self.verify_manual(command)
        print("Verification Is Done !")

    #-----------------------------------------------------------------------------------------
    def search_command_manual(self, answer1):
        self.last_search = answer1
        command_file = f"CommandManuals/{answer1}.xml"
        if os.path.exists(command_file):
            print(f"Command manual for '{answer1}' exists:")

            while True:
                print("\nSelect a part to display:")
                print("1. Full Manual")
                print("2. Command Description")
                print("3. Version History")
                print("4. Example")
                print("5. Execute Example")
                print("6. Related Commands")
                print("7. Go Back to Main Menu")

                part_choice = input("Enter your choice (1-7): ")

                if part_choice == "1":
                    with open(command_file, "r") as file:
                        print(file.read())
                elif part_choice == "2":
                    self.display_part(command_file, "CommandDescription")
                elif part_choice == "3":
                    self.display_part(command_file, "VersionHistory")
                elif part_choice == "4":
                    self.display_part(command_file, "Example")
                elif part_choice == "5":
                    self.display_part(command_file, "ExecuteExample")
                elif part_choice == "6":
                    self.display_part(command_file, "RelatedCommands")
                elif part_choice == "7":
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 7.")

        else:
            # List all XML files in the "CommandManuals" directory
            files = glob.glob("CommandManuals/*.xml")

            #files that contain the specified search term in their names
            matching_files = [file for file in files if answer1 in os.path.basename(file)]

            if matching_files:
                print(f"Found matches for '{answer1}' in the following files:")
                for match in matching_files:
                    print(os.path.basename(match))
            else:
                print("No matches found! Files in Command Manuals:")
                for file in os.listdir("CommandManuals"):
                    print(file)

    #-----------------------------------------------------------------------------------------
    def display_part(self, command_file, part_tag):
        with open(command_file, "r") as file:
            xml_content = file.read()

        start_tag = f"<{part_tag}>"
        end_tag = f"</{part_tag}>"

        start_index = xml_content.find(start_tag)
        end_index = xml_content.find(end_tag)

        if start_index == -1 or end_index == -1 or end_index <= start_index:
            print(f"Error: Unable to find {part_tag} tags in {command_file}.")
            return

        part_content = xml_content[start_index + len(start_tag):end_index].strip()
        print(f"\n{part_tag}:\n{part_content}")

    #-----------------------------------------------------------------------------------------
    def get_recommendations(self, command):
        command_recommendations_key = f"{command}_recommendations"
        if command_recommendations_key in globals():
            return globals()[command_recommendations_key]
        else:
            return []

    #-----------------------------------------------------------------------------------------
    def recommend_commands(self, last_search):
        if last_search:
            recommendations = self.get_recommendations(last_search)
            if recommendations:
                print(f"Recommendations for '{last_search}':")
                for recommendation in recommendations:
                    print(recommendation)
            else:
                print(f"No recommendations found for '{last_search}'!")
        else:
            print("No last search!")
            
#*******************************************************************************************************************            
class CommandManual:
    def __init__(self, commandName, Description, Version, Example, ExecuteExample, RelatedCommands):
        self.commandName = commandName
        self.Description = Description
        self.Version = Version
        self.Example = Example
        self.ExecuteExample = ExecuteExample
        self.RelatedCommands = RelatedCommands

     #-----------------------------------------------------------------------------------------
    def to_xml(self):
        #the root element for the XML structure
        command_manual = ET.Element("CommandManual")
        #sub-elements for each attribute
        ET.SubElement(command_manual, "CommandName").text = str(self.commandName)
        ET.SubElement(command_manual, "CommandDescription").text = str(self.Description)
        ET.SubElement(command_manual, "VersionHistory").text = str(self.Version)
        ET.SubElement(command_manual, "Example").text = str(self.Example)
        ET.SubElement(command_manual, "ExecuteExample").text = str(self.ExecuteExample)
        ET.SubElement(command_manual, "RelatedCommands").text = str(self.RelatedCommands)
 
        #the root element for the entire XML document
        manuals = ET.Element("Manuals")
        manuals.append(command_manual)
        
        # Return the XML structure as an ElementTree object
        return ET.ElementTree(manuals)

#*******************************************************************************************************************
class XmlSerializer:
    #static method 'serializ' for converting a CommandManual object into an XML
    @staticmethod
    def serialize(command_manual):
        # Get the root element of the XML structure
        manual_root = command_manual.to_xml().getroot()

        #Convert the XML root element to a byte string
        xml_string = ET.tostring(manual_root, encoding="utf-8").decode()
        return xml_string

       
#*******************************************************************************************************************

#create instance of the CommandManualGenerator class 
command_manual_generator = CommandManualGenerator()

while True:
        print("\nMenu:")
        print("1. Generate Manuals")
        print("2. Verify Manuals")
        print("3. Search Command Manual")
        print("4. Recommend Commands")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            command_manual_generator.generate_manuals()
        elif choice == "2":
            command_manual_generator.verify_manuals()
        elif choice == "3":
            answer1 = input("Enter the command name or topic: ")
            command_manual_generator.search_command_manual(answer1)
        elif choice == "4":
            command_manual_generator.recommend_commands(command_manual_generator.last_search)
        elif choice == "5":
            print("Exiting the program. Goodbye!")
            exit(0)
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
