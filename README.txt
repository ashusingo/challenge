Description:- Python based USER data API
Dependency:- 
	Python 2.7
	Postgres 11.x
Assumption:-
	Database should be already created in the postgres server. Our code will handle the creation of table.
	Code can read the database related information from environment variable. If It is not available then it read the constant file. 
	User can modify the constant.py based on database configuration. 
	
How to start:- 
	First need to install dependency. 
	go to the folder where code is kept. 
	cd <Folder locaion>
	pip install -r requirement.txt
	python server.py

About code flow:-
	Server.py is the main code handling all the rest API.
	dblayer.py is database interaction layer for insert,select and update.
	constant.py is constant file for config values. 
	
	cd <Folder location>
	python server.py
	
	It will start the server 
	http://127.0.0.1:9001
	Supported API:- 
	POST :- 
	
	http://127.0.0.1:9001/users
	http://127.0.0.1:9001/login
	 
	http://127.0.0.1:9001/stop (To Stop the server)
	Patch:-
	http://127.0.0.1:9001/users/<id>

For Any question/clarification Please ping me :- ashutosh100ankit@gmail.com
You can access the test recording :- https://Dell.zoom.us/rec/share/4zNmx_23eMbXMekUFChZ3tBtvsTBBVz5m4mtLYn8e2BQsaKUFQIlQ8B088GaKrCN.4Zbt355_X9w-1ov7 Passcode: p8QB55Y%

