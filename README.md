# placement
Placement Portal using python and django

This is project usign which college TPO(Training and Placement cell) can maintain all the data of students which are in the 
placement process of all years. It makes work quite easy as it is one application which can be used by diffrent users as well.
We don't need to maintain excel sheets for different years and students as well. It makes data maintainece quite fast and
easy. Future scope of this project is that it can be extended to students and recruiters as well, so that recruiters
can see profiles of students and students can update their profiles which does not include any TPO interaction. It makes 
placement process easier and smoother for future.

To run this project please follow these steps :

Step 1 - Create a new folder

Step 2 - select current directory as the folder which you have created.

Step 3 - create a virtual enviornment of python3 using the command "python3 -m venv ."

Step 4 - clone git repository using the command "git clone https://github.com/saket9000/placement.git".

Step 5 - activate virtual enviornment using command "source bin/activate".

Step 6 - create a mysql database and replace the credentials in settings.py file.

	 update the Database name, user name, and password there


Step 7 - goto to "placement" directory

Step 8 - Create a new folder with name "media" and inside that directory make another directory with name "profile-images".

Step 9 - Also update settings.py file with the MAIL SETTINGS from line 143 to 149.
	
	 #These are the setting for Gmail
	 DEFAULT_FROM_EMAIL = '****' //EMAIL ADDRESS
	 SERVER_EMAIL = '****' //EMAIL ADDRESS
 	 EMAIL_HOST = 'smtp.gmail.com'
	 EMAIL_PORT = 587
	 EMAIL_HOST_USER = '****' //EMAIL ADDRESS
	 EMAIL_HOST_PASSWORD = '****' //PASSWORD

Step 10 - Now we will install Django and other dependencies of the project, run command "pip install -r requirements.txt"

	 -create a super user using "python manage.py createsuperuser"
		-choose you own user name and password for login

	 -write command "python manage.py migrate"


Step 11 - Now we can run our project by "python manage.py runserver".

Step 12 - Goto localhost and login using the credentials.
