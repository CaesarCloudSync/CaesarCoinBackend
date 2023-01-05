# Python program to create Blockchain

# For timestamp
import datetime
import socket
# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain
import json

# Flask is for creating the web
# app and jsonify is for
# displaying the blockchain
from flask import Flask, jsonify,request,send_file,send_from_directory,render_template
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from blockchain import Blockchain
from csv_to_db import ImportCSV
from models import CompanyUsers,ContributorUsers 
from bson.objectid import ObjectId # 
import datetime
import time
import hashlib
import shutil
import os
import io
import gridfs
# Creating the Web
# App using flask
app = Flask(__name__)
jwt = JWTManager(app)
importcsv = ImportCSV("CaesarCoinDB")
caesarfs = gridfs.GridFS(importcsv.gridfs)
app.config['JWT_SECRET_KEY'] = "Peter Piper picked a peck of pickled peppers, A peck of pickled peppers Peter Piper picked, If Peter Piper picked a peck of pickled peppers,Where's the peck of pickled peppers Peter Piper picked" #'super-secret'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
# Create the object
# of the class blockchain
blockchain = Blockchain()

# Mining a new block
# TODO Sent by Quota Poster
# TODO Sent by Contributor
# TODO Two Factor Authentication
# TODO Allow each device to make local honey pot to send to
def authenticate_blockchain_membership(current_user,blockchain_name_id,blockchain_password):
	blockchaininfo_exists = importcsv.db.blockchaininfo.find_one({"blockchain_name_id": blockchain_name_id})
	if blockchaininfo_exists:
		blockchaininfo_db = importcsv.db.blockchaininfo.find({"blockchain_name_id": blockchain_name_id})[0]
		if blockchaininfo_db["privilege"] == "private":
			if blockchain_password == blockchaininfo_db["blockchain_password"]:
				if current_user in blockchaininfo_db["blockchain_members"]:
					return {"message":"user is already a member of this blockchain."}
				elif current_user not in blockchaininfo_db["blockchain_members"]:
					return {"message":"member not in private blockchain."}
			elif blockchain_password  != blockchaininfo_db["blockchain_password"]:
				return {"message":"incorrect password, not authorized to join."}
		elif blockchaininfo_db["privilege"] == "public":
			if current_user in blockchaininfo_db["blockchain_members"]:
				return {"message":"user is already a member of this blockchain."}
			elif current_user not in blockchaininfo_db["blockchain_members"]:
				return {"message":"member not in public blockchain."}

	elif not blockchaininfo_exists:
		return {"message":"blockchain does not exist."}
@app.route('/', methods=['GET'])
@cross_origin()
def caesarcoinhome():
    return render_template("caesarcoinhome.html")
	 #"CaesarCoin, This is the Caesar Coin Blockchain."
# Function for contributor
@app.route("/seed")
@cross_origin()
def seed():
    return render_template("caesarseed.html")
# Function for quota poster
@app.route("/torrent")
@cross_origin()
def torrent():
    return render_template("caesartorrent.html")
# FUnction for contributor
@app.route("/storemagneturi",methods=["GET","POST"])
@cross_origin()
@jwt_required()
def storemagneturi():
	current_user = get_jwt_identity()
	if current_user:
		try:
			torrentdetails = request.get_json()
			# TODO create a block for the blockchain without long mining and just reward them with a larger cut of coin.
			companyid = str(hashlib.sha256(torrentdetails["companyname"].encode()).hexdigest())
			quota_accepted_exists = importcsv.db.quotas_accepted.find_one({"companyid": companyid})
			if quota_accepted_exists:
				quota_company_accepted = importcsv.db.quotas_accepted.find({"companyid": companyid})[0]
				# Get quota hash value
				quota_exists = importcsv.db.quotas.find_one({"companyid": companyid})
				if quota_exists:
					quotahashvalue = ""
					quotas_db= importcsv.db.quotas.find({"companyid": companyid})[0]
					for quota in quotas_db["quotas"]:
						if quota["title"] == torrentdetails["quotaname"]:
							quotahashvalue += quota["quotahashvalue"]
					if len(quotahashvalue) > 0:			
						try:
							if current_user in quota_company_accepted[quotahashvalue]["contributors"]:
								magneturi_exists = importcsv.db.quotamagneturis.find_one({"companyid": companyid})
								#original_contributor_string = str(current_user)+ companyid + torrentdetails["quotaname"] + torrentdetails["torrentfilename"] + torrentdetails["torrentmagneturi"]
								#original_contributor_hash = str(hashlib.sha256(original_contributor_string.encode()).hexdigest())
								if magneturi_exists:

									try:
										magneturi_db = importcsv.db.quotamagneturis.find({"companyid": companyid})[0]
										jsonstore = {"quotaname":torrentdetails["quotaname"],"torrentfilename":torrentdetails["torrentfilename"],"torrentmagneturi":torrentdetails["torrentmagneturi"],"original_contributor_name":torrentdetails["contributorname"],"filesize":torrentdetails["filesize"]} #"original_contributor_hash":original_contributor_hash,
										if jsonstore in magneturi_db["quotas"]:
											return {"message":"magneturi already exists"},200
										elif jsonstore not in magneturi_db["quotas"]:
											magneturi_db["quotas"].append(jsonstore)
											importcsv.db.quotamagneturis.replace_one({"companyid": companyid},magneturi_db)
											return {"message":"magneturi added"},200
									except KeyError as kexe:
										return {"error":f"magneturi exists but: {type(kexe)},{kexe}"},200
								elif not magneturi_exists:
									importcsv.db.quotamagneturis.insert_one({"companyid":companyid,"quotas":[{"quotaname":torrentdetails["quotaname"],"torrentfilename":torrentdetails["torrentfilename"],"torrentmagneturi":torrentdetails["torrentmagneturi"],"original_contributor_name":torrentdetails["contributorname"],"filesize":torrentdetails["filesize"]}]}) #"original_contributor_hash":original_contributor_hash,
									return {"message":"magneturi stored."},200
							elif current_user not in quota_company_accepted[quotahashvalue]["contributors"]:
								return {"error":"contributor is not authorized to send data to this quota."},200
						except KeyError as kex:
							return {"error":f"company or contributor doesn't exist.{type(kex)},{kex}"},200
				elif len(quotahashvalue) == 0:
					return {"error":"quota does not exist."},200
			elif not quota_accepted_exists:
				return {"error":"company acceptance collection does not exist."},200
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"},400
  
@app.route("/getmagneturi",methods=["GET","POST"])
@cross_origin()
@jwt_required()
def getmagneturi():
	current_user = get_jwt_identity()
	if current_user:
		try:
			torrentdetails = request.get_json()
			# TODO Store in db
			# companyid, quotahashvalue, 
			#  { torrentfilename: "main.jpeg", torrentmagneturi: "magnet:?xt=urn:btih:5054704b0ab85ce6ddbe2a9e8b75e7a60d72f8e3&dn=main.jpeg&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Fexplodie.org%3A6969&tr=udp%3A%2F%2Ftracker.empire-js.us%3A1337&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.openwebtorrent.com" }
			# company -> quotas -> [{"quota":"<name>",torrentfile:"file",magneturi}]
			companyid = str(hashlib.sha256(torrentdetails["companyname"].encode()).hexdigest())
			quota_accepted_exists = importcsv.db.quotas_accepted.find_one({"companyid": companyid})
			if quota_accepted_exists:
				quota_company_accepted = importcsv.db.quotas_accepted.find({"companyid": companyid})[0]
				# Get quota hash value
				quota_exists = importcsv.db.quotas.find_one({"companyid": companyid})
				if quota_exists:
					quotahashvalue = ""
					quotas_db= importcsv.db.quotas.find({"companyid": companyid})[0]
					for quota in quotas_db["quotas"]:
						if quota["title"] == torrentdetails["quotaname"]:
							quotahashvalue += quota["quotahashvalue"]
					if len(quotahashvalue) > 0:		
						try:
							if current_user in quota_company_accepted[quotahashvalue]["contributors"]:
								magneturi_exists = importcsv.db.quotamagneturis.find_one({"companyid": companyid})
								if magneturi_exists:
									try:
										selected_quota = []
										magneturi_db = importcsv.db.quotamagneturis.find({"companyid": companyid})[0]
										for quota in magneturi_db["quotas"]:
											if quota["quotaname"] == torrentdetails["quotaname"] and quota["torrentfilename"] == torrentdetails["torrentfilename"]:
												#del quota["original_contributor_hash"]
												selected_quota.append(quota)
											else:
												continue
										if len(selected_quota) == 0:
											return {"error":"quota or torrent file doesn't exist"},200
										elif len(selected_quota) > 0:
											return selected_quota[0],200
									except KeyError as kexe:
										return {"error":f"magneturi exists but: {type(kexe)},{kexe}"},200
								elif not magneturi_exists:
									return {"message":"magneturi does not exist."},400
							elif current_user not in quota_company_accepted[quotahashvalue]["contributors"]:
								return {"error":"contributor is not authorized to fetch data to this quota."},200
						except KeyError as kex:
							return {"error":f"company or contributor doesn't exist.{type(kex)},{kex}"},400
						
					elif len(quotahashvalue) == 0:
						pass
			elif not quota_accepted_exists:
				return {"message":"company acceptance collection does not exist."},200
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"}

@app.route("/getallmagneturi",methods=["GET"])
@cross_origin()
@jwt_required()
def getallmagneturi():
	current_user = get_jwt_identity()
	if current_user:
		try:
			magneturi_exists = importcsv.db.quotamagneturis.find_one({"companyid": current_user})
			if magneturi_exists:
				magneturi_db = importcsv.db.quotamagneturis.find({"companyid": current_user})[0]
				
				return {"quotamagneturis":magneturi_db["quotas"]}
			elif not magneturi_exists:
				return {"message":"no torrent files have been uploaded yet."}
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"}
# Both Contributor and quota poster
@app.route('/create_blockchain', methods=['POST'])
@cross_origin()
@jwt_required()
def create_blockchain():
	current_user = get_jwt_identity()
	if current_user:
		try:
			# current_user,name_of_block_chain, prvilege - public or private
			create_block_details = request.get_json()
			
			blockchain_name_id = str(hashlib.sha256(create_block_details["blockchain_name"].encode()).hexdigest())
			if create_block_details["blockchain_privilege"] == "private":
				blockchain_password = str(hashlib.sha256(create_block_details["blockchain_password"].encode()).hexdigest())
			elif create_block_details["blockchain_privilege"] == "public":
				blockchain_password = "none"
			
			blockchaininfo_exists = importcsv.db.blockchaininfo.find_one({"blockchain_name_id": blockchain_name_id})
			if blockchaininfo_exists:
				return {"message":"blockchain already exists"},200
			
			elif not blockchaininfo_exists:
				importcsv.db.blockchaininfo.insert_one({"blockchain_name_id": blockchain_name_id,"blockchain_members":[current_user],"privilege":create_block_details["blockchain_privilege"],"blockchain_password":blockchain_password})
				genesis_block = {"index": 0,"transactions": [],"timestamp": time.time(),"previous_hash": "0","nonce": 0}
				block_string = json.dumps(genesis_block, sort_keys=True)
				genesis_block["hash"] = hashlib.sha256(block_string.encode()).hexdigest()
				importcsv.db.blockchains.insert_one({"blockchain_name_id":blockchain_name_id,"chain":[genesis_block]})
				#blockchain_token = create_access_token(identity=blockchain_name_id)
				return {"message":"blockchain created"},200 #{"blockchain_access_token":blockchain_token},200
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"},400

		
@app.route('/join_blockchain', methods=['POST'])
@cross_origin()
@jwt_required()
def join_blockchain():
	current_user = get_jwt_identity()
	if current_user:
		try:
			join_block_details = request.get_json()
			blockchain_name_id = str(hashlib.sha256(join_block_details["blockchain_name"].encode()).hexdigest())
			try:
				blockchain_password = str(hashlib.sha256(join_block_details["blockchain_password"].encode()).hexdigest())
			except KeyError as kex:
				blockchain_password = None
			blockchaininfo_exists = importcsv.db.blockchaininfo.find_one({"blockchain_name_id": blockchain_name_id})
			if blockchaininfo_exists:
				blockchaininfo_db = importcsv.db.blockchaininfo.find({"blockchain_name_id": blockchain_name_id})[0]
				if blockchaininfo_db["privilege"] == "private":
					if blockchain_password == blockchaininfo_db["blockchain_password"]:
						if current_user in blockchaininfo_db["blockchain_members"]:
							return {"message":"user is already a member of this blockchain."}
						elif current_user not in blockchaininfo_db["blockchain_members"]:
							blockchaininfo_db["blockchain_members"].append(current_user)
							importcsv.db.blockchaininfo.replace_one({"blockchain_name_id": blockchain_name_id},blockchaininfo_db)
							return {"message":"member added to blockchain."}
					elif blockchain_password  != blockchaininfo_db["blockchain_password"]:
						return {"error":"incorrect password, not authorized to join."}
				elif blockchaininfo_db["privilege"] == "public":
					if current_user in blockchaininfo_db["blockchain_members"]:
						return {"message":"user is already a member of this blockchain."}
					elif current_user not in blockchaininfo_db["blockchain_members"]:
						blockchaininfo_db["blockchain_members"].append(current_user)
						importcsv.db.blockchaininfo.replace_one({"blockchain_name_id": blockchain_name_id},blockchaininfo_db)
						return {"message":"member added to blockchain."}

			elif not blockchaininfo_exists:
				return {"error":"blockchain does not exist."}
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"}
@app.route('/get_last_block', methods=['POST'])
@cross_origin()
@jwt_required()
def get_last_block():
	current_user = get_jwt_identity()
	if current_user:
		try:
			blockjson = request.get_json()
			blockchain_name_id = str(hashlib.sha256(blockjson["blockchain_name"].encode()).hexdigest())
			try:
				blockchain_password = str(hashlib.sha256(blockjson["blockchain_password"].encode()).hexdigest())
			except KeyError as kex:
				blockchain_password = None
			blockchaininfo_exists = importcsv.db.blockchaininfo.find_one({"blockchain_name_id": blockchain_name_id})
			if blockchaininfo_exists:
				blockchaininfo_db = importcsv.db.blockchaininfo.find({"blockchain_name_id": blockchain_name_id})[0]
				if blockchaininfo_db["privilege"] == "private":
					if blockchain_password == blockchaininfo_db["blockchain_password"]:
						blockchain_db = importcsv.db.blockchains.find({"blockchain_name_id": blockchain_name_id})[0]
						return blockchain_db["chain"][-1]
					elif blockchain_password != blockchaininfo_db["blockchain_password"]:
						return {"error":"incorrect password, not authorized to get last black of the blockchain."}
				elif blockchaininfo_db["privilege"] == "public":
					pass
			elif not blockchaininfo_exists:
				return {"error":"blockchain does not exist."}
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"}


@app.route('/store_block', methods=['POST'])
@cross_origin()
@jwt_required()
def store_block():
	current_user = get_jwt_identity()
	if current_user:
		try:
			blockjson = request.get_json()
			blockchain_name_id = str(hashlib.sha256(blockjson["blockchain_name"].encode()).hexdigest())
			blockdetails = blockjson["block"]
			try:
				blockchain_password = str(hashlib.sha256(blockjson["blockchain_password"].encode()).hexdigest())
			except KeyError as kex:
				blockchain_password = None
			try:
				index = blockdetails["index"]
				transactions = blockdetails["transactions"]
				transactions[-1]["recipient"] = str(hashlib.sha256(transactions[-1]["recipient"].encode()).hexdigest())
				timestamp = blockdetails["timestamp"]
				previous_hash = blockdetails["previous_hash"]
				nonce = blockdetails["nonce"]
				hashvalue = blockdetails["hash"]
			except KeyError as kex:
				return {"error":"blocks format is not correct"}
			blockchaininfo_exists = importcsv.db.blockchaininfo.find_one({"blockchain_name_id": blockchain_name_id})
			if blockchaininfo_exists:
				blockchaininfo_db = importcsv.db.blockchaininfo.find({"blockchain_name_id": blockchain_name_id})[0]
				if blockchaininfo_db["privilege"] == "private":
					if blockchain_password == blockchaininfo_db["blockchain_password"]:
						if current_user in blockchaininfo_db["blockchain_members"]:
							blockchain_db = importcsv.db.blockchains.find({"blockchain_name_id": blockchain_name_id})[0]
							blockchain_db["chain"].append({"index": index,"transactions": transactions,"timestamp":timestamp,"previous_hash": previous_hash,"nonce": nonce,"hash":hashvalue})
							importcsv.db.blockchains.replace_one({"blockchain_name_id": blockchain_name_id},blockchain_db)
							return {"message":"block added to blockchain"}
						elif current_user not in blockchaininfo_db["blockchain_members"]:
							return {"message":"not a member of the blockchain."}
					elif blockchain_password  != blockchaininfo_db["blockchain_password"]:
						return {"error":"incorrect password, not authorized to add a block to the blockchain."}
				elif blockchaininfo_db["privilege"] == "public":
					if current_user in blockchaininfo_db["blockchain_members"]:
						blockchain_db = importcsv.db.blockchains.find({"blockchain_name_id": blockchain_name_id})[0]
						blockchain_db["chain"].append({"index": index,"transactions": transactions,"timestamp":timestamp,"previous_hash": previous_hash,"nonce": nonce,"hash":hashvalue})
						importcsv.db.blockchains.replace_one({"blockchain_name_id": blockchain_name_id},blockchain_db)
						return {"message":"block added to blockchain"}
					elif current_user not in blockchaininfo_db["blockchain_members"]:
						return {"message":"not a member of the blockchain."}
			elif not blockchaininfo_exists:
				return {"error":"blockchain does not exist."}
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"}





@app.route('/quotapostersignup', methods=['POST'])
@cross_origin()
def quotapostersignup():
	# Parameters: {"company":"Google","email":"amari.lawal05@gmail.com","password":"kya63amari"}
	try:
		data = request.get_json()
		companyid = str(hashlib.sha256(data["company"].encode()).hexdigest())
		data["id"] = ObjectId()
		data["companyid"] = companyid
		user = CompanyUsers(**data)
		signupdata = user.to_bson() 
		
		companyid_exists = importcsv.db.quotaposterusers.find_one({"companyid": companyid})
		if companyid_exists:
			return jsonify({"message": "Email already exists"}) ,400
		elif not companyid_exists:
			importcsv.db.quotaposterusers.insert_one(signupdata)
			access_token = create_access_token(identity=signupdata["companyid"])
			callback = {"status": "success","id": str(signupdata["_id"]),"access_token":access_token}
			return callback,200
	except Exception as ex:
		error_detected = {"error": "error occured","errortype":type(ex), "error": str(ex)}
		return error_detected,400
	

@app.route('/quotapostersignin', methods=['POST'])
@cross_origin()
def quotapostersignin():
	# Login API
	# {"company":"Google","password":"kya63amari"}
	try:
		def provide_access_token(login_details):
			email_exists = list(importcsv.db.quotaposterusers.find({"companyid": login_details["companyid"]}))[0]
			encrypted_password =  hashlib.sha256(login_details["password"].encode('utf-8')).hexdigest()
			if email_exists["password"] == encrypted_password:
				access_token = create_access_token(identity=email_exists["companyid"])
				return access_token
			else:
				return "Wrong password"
		login_details = request.get_json()
		companyid = str(hashlib.sha256(login_details["company"].encode()).hexdigest())
		login_details["companyid"] = companyid
		companyid_exists = importcsv.db.quotaposterusers.find_one({"companyid": companyid})
		if companyid_exists:
			access_token = provide_access_token(login_details)
			if access_token == "Wrong password":
				return jsonify({"message": "The username or password is incorrect."}),400
			else:
				return jsonify({"access_token": access_token}), 200
		return jsonify({"message": "The username or password is incorrect."}),400
	
	except Exception as ex:
		return jsonify({"error": f"{type(ex)} {str(ex)}"})
	# Token: JWT Token
	# Parameters: {"company":"<text>" -> "companyid":"<hash>","password":"<text>"}
	# Return: {"access_token":"<text|token>"}
	

@app.route('/contributorsignup', methods=['POST'])
@cross_origin()
def contributorsignup():
	# Token: JWT Token
	# Parameters: {"contributor":"palondomus","email":"amari.lawal@gmail.com","password":"kya63amari"}
	try:
		data = request.get_json()
		contributorid = str(hashlib.sha256(data["contributor"].encode()).hexdigest())
		data["id"] = ObjectId()
		data["contributorid"] = contributorid
		user = ContributorUsers(**data)
		signupdata = user.to_bson() 
		
		contributorid_exists = importcsv.db.contributorusers.find_one({"contributorid": contributorid})
		if contributorid_exists:
			return jsonify({"message": "Email already exists"}) , 400
		elif not contributorid_exists:
			importcsv.db.contributorusers.insert_one(signupdata)
			access_token = create_access_token(identity=signupdata["contributorid"])
			callback = {"status": "success","id": str(signupdata["_id"]),"access_token":access_token}
			return callback,200
	except Exception as ex:
		error_detected = {"error": "error occured","errortype":type(ex), "error": str(ex)}
		return error_detected,400

@app.route('/contributorsignin', methods=['POST'])
@cross_origin()
def contributorsignin():
	# Token: JWT Token
	# Parameters:{"contributor":"palondomus","password":"kya63amari"}
	# Return: {"access_token":"<text|token>"}
	try:
		def provide_access_token(login_details):
			email_exists = list(importcsv.db.contributorusers.find({"contributorid": login_details["contributorid"]}))[0]
			encrypted_password =  hashlib.sha256(login_details["password"].encode('utf-8')).hexdigest()
			if email_exists["password"] == encrypted_password:
				access_token = create_access_token(identity=email_exists["contributorid"])
				return access_token,200
			else:
				return "Wrong password",400
		login_details = request.get_json()
		hostname = socket.gethostname()    
		IPAddr = socket.gethostbyname(hostname)  
		print(IPAddr)  
		contributorid = str(hashlib.sha256(login_details["contributor"].encode()).hexdigest())
		login_details["contributorid"] = contributorid
		contributorid_exists = importcsv.db.contributorusers.find_one({"contributorid": contributorid})
		if contributorid_exists:
			access_token = provide_access_token(login_details)
			if access_token == "Wrong password":
				return jsonify({"message": "The username or password is incorrect."}),400
			else:
				return jsonify({"access_token": access_token[0]}), 200
		return jsonify({"message": "The username or password is incorrect."}),400
	
	except Exception as ex:
		return jsonify({"error": f"{type(ex)} {str(ex)}"}),400

# TODO Done by the Quota Poster
@app.route('/create_quota', methods=['POST'])
@cross_origin()
@jwt_required()
def create_quota():
	current_user = get_jwt_identity() 
	if current_user:
		try:
			# TODO Store whether they want send the datasets publicly or privately. 
			# If publicy - will use torrent. if privatly will use dropbox
			# public - Pros | Cons
			# Passive generation of coin for each seeder made for the dataset, so that it can be distributed worldwide
			# Initial contributor will become seeder, then another person can just download it to either use it then become seeder.
			# Flow -> Use dataset -> Become seeder -> Use dataset -> become seeder -> Finally the quota poster will get what they wanted.
			# This means that all datascientists will have accces of the data from all over the world as a shared inititave

			# Private - Pros | Cons
			# If data is confidentital then it can be sent privatel to the quota poster. The contriutor will only generate a fixed one time amount of coin and 
			# others shouldn't have access unless contributor externally distributes.
			# TODO {"company":"<text>","title":"<text>","subject":"<text>","description":"<text>","thumbnail":"<img>","dataquota":"<int>","databaseurlendpoint":"<apiendpoint>"}
			quotaparameters = request.get_json()
			#{"comapny":"","quotas":[{"title":"",""}]}
			companyid = current_user #str(hashlib.sha256(quotaparameters["company"].encode()).hexdigest())
			companyid_exists = importcsv.db.quotaposterusers.find_one({"companyid": companyid})
			if companyid_exists:
				quotaid_exists = importcsv.db.quotas.find_one({"companyid": companyid})
				if quotaid_exists:
					companyquota = list(importcsv.db.quotas.find({"companyid": companyid}))[0]
					#print(companyquota)
					#print(quotaparameters["quotas"][0] )
					hashsetup = quotaparameters["quotas"][0]["title"]
					hashvalue = str(hashlib.sha256(hashsetup.encode()).hexdigest())
					quotaparameters["quotas"][0]["quotahashvalue"] = hashvalue
					del companyquota["_id"]
					if quotaparameters["quotas"][0] in companyquota["quotas"]:
						return {"message":"quota already exists"}
					elif quotaparameters["quotas"][0] not in companyquota["quotas"]:
						companyquota["quotas"].append(quotaparameters["quotas"][0])
						importcsv.db.quotas.replace_one({"companyid": companyid},companyquota)
						return {"message":"quota added"},200


				
				elif not quotaid_exists:
					#del quotaparameters["company"]
					quotaparameters["companyid"] = current_user
					hashsetup = quotaparameters["quotas"][0]["title"]
					hashvalue = str(hashlib.sha256(hashsetup.encode()).hexdigest())
					quotaparameters["quotas"][0]["quotahashvalue"] = hashvalue
					importcsv.db.quotas.insert_one(quotaparameters)
					return {"message":"quota created"},200
			elif not companyid_exists:
				return {"error":f"{current_user} is not quotaposter"},400
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"},400
		
# TODO Fetched for Quota on website
@app.route('/get_quotas', methods=['GET'])
@cross_origin()
def get_quotas():
	#current_user = get_jwt_identity() 
	#if current_user:
	company = request.args.get("company")
	try:
		companyid = str(hashlib.sha256(company.encode()).hexdigest())
		quotaid_exists = importcsv.db.quotas.find_one({"companyid": companyid})
		if quotaid_exists:
			companyquota = list(importcsv.db.quotas.find({"companyid": companyid}))[0]
			#print(companyquota)
			del companyquota["_id"]
			return companyquota,200
		elif not quotaid_exists:
			return {"error":"quotas doesn't exist"},200
		
	except Exception as ex:
		return {"error":f"{type(ex)},{ex}"},400

	# TODO {"companyid":"<hash>","company":"<text>","title":"<text>","subject":"<text>","description":"<text>","thumbnail":"<img>","dataquota":"<int>","databaseurlendpoint":"<apiendpoint>"}
	# TODO return {"company":"<text>","title":"<text>","subject":"<text>","description":"<text>","thumbnail":"<img>","dataquota":"<int>"}

	pass
# TODO Sent by Contributor
@app.route('/store_quota_contribution_request', methods=['POST'])
@cross_origin()
@jwt_required()
def store_quota_contribution_request():
	current_user = get_jwt_identity() 
	if current_user:
		try:
			quota_request = request.get_json()
			companyid = str(hashlib.sha256(quota_request["company"].encode()).hexdigest())
			quota_title = str(hashlib.sha256(quota_request["quota"].encode()).hexdigest())
			
			quota_poster_exists = importcsv.db.quotaposterusers.find_one({"companyid": companyid})
			if quota_poster_exists:
				quota_request_exists = importcsv.db.quota_contribution_requests.find_one({"companyid": companyid})
				if quota_request_exists:
					quota_request_db = importcsv.db.quota_contribution_requests.find({"companyid": companyid})[0]
					try:
						if current_user in quota_request_db["quotas"][quota_title]:
							return {"message":"quota contribution from this user already exists for this company."}
						elif current_user not in quota_request_db["quotas"][quota_title]:
							quota_request_db["quotas"][quota_title].append(current_user)
							importcsv.db.quota_contribution_requests.replace_one({"companyid": companyid},quota_request_db)
							return {"message":"quota contribution request add."},200
					except KeyError as kex:
						# Maybe do it so that it checks from the quota collection.
						quota_request_db["quotas"].update({quota_title:[current_user]})
						importcsv.db.quota_contribution_requests.replace_one({"companyid": companyid},quota_request_db)
						return {"message":"new quota title added"},200		
				
				elif not quota_request_exists:
					importcsv.db.quota_contribution_requests.insert_one({"companyid":companyid,"quotas":{quota_title:[current_user]}})
					return {"message":"quota contribution request created."},200
			elif not quota_poster_exists:
				return {"message":"company doesn't exist"},200		

		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"},400

	# {"companyid"}
	# Token: JWT Token
	# Parameters: {"companyid":"<hash>","userid":"<hash>",}
	# Store DB - pending_quota_requests: {"companyid":"<hash>","userid":"<hash>","permision":"pending"}

#	pass
# TODO Sent by Quota Poster
@app.route('/verify_quota_contribution', methods=['POST'])
@cross_origin()
@jwt_required()
def verify_quota_contribution():
	current_user = get_jwt_identity() 
	if current_user:
		try:
			quota_choice = request.get_json()
			contributor = str(hashlib.sha256(quota_choice["contributor"].encode()).hexdigest())
			choice = quota_choice["choice"].lower()
			quota_title = str(hashlib.sha256(quota_choice["quota_title"].encode()).hexdigest())
			quota_request_exists = importcsv.db.quota_contribution_requests.find_one({"companyid": current_user})
			if quota_request_exists:
				quota_request_db = importcsv.db.quota_contribution_requests.find({"companyid": current_user})[0]
				if contributor in quota_request_db["quotas"][quota_title]:
					# Acceptence part
					if choice == "y":
						quota_accepted_exists = importcsv.db.quotas_accepted.find_one({"companyid": current_user})
						quotas_rejected_exists = importcsv.db.quotas_rejected.find_one({"companyid": current_user})
						if quotas_rejected_exists:
							quota_rejected_db = importcsv.db.quotas_rejected.find({"companyid": current_user})[0]
							if contributor in quota_rejected_db[quota_title]["contributors"]:
								return {"message":"contributor has already been rejected."}


						if not quota_accepted_exists:
							importcsv.db.quotas_accepted.insert_one({"companyid":current_user,quota_title:{"contributors":[contributor]}})
							quota_request_db["quotas"][quota_title].remove(contributor)
							importcsv.db.quota_contribution_requests.replace_one({"companyid": current_user},quota_request_db)
							return {"message":"contributor was created"},200
						elif quota_accepted_exists:						
							try:
								quota_accepted_db = importcsv.db.quotas_accepted.find({"companyid": current_user})[0]
								if contributor not in quota_accepted_db[quota_title]["contributors"]:
									quota_accepted_db[quota_title]["contributors"].append(contributor)
									importcsv.db.quotas_accepted.replace_one({"companyid": current_user},quota_accepted_db)
									quota_request_db["quotas"][quota_title].remove(contributor)
									importcsv.db.quota_contribution_requests.replace_one({"companyid": current_user},quota_request_db)
									return {"message":"contributor was accepted."},200
								elif contributor in quota_accepted_db[quota_title]["contributors"]:
									return {"message":"contributor already accepted."},200
							except KeyError as kex:
								return {"error":"quota does not exist"},200
					# Rejection Part
					elif choice == "n":
						quotas_rejected_exists = importcsv.db.quotas_rejected.find_one({"companyid": current_user})
						quotas_accepted_exists = importcsv.db.quotas_accepted.find_one({"companyid": current_user})
						if quotas_accepted_exists:
							quotas_accepted_db = importcsv.db.quotas_accepted.find({"companyid": current_user})[0]
							if contributor in quotas_accepted_db[quota_title]["contributors"]:
								return {"message":"contributor has already been accepted."}

						if not quotas_rejected_exists:
							importcsv.db.quotas_rejected.insert_one({"companyid":current_user,quota_title:{"contributors":[contributor]}})
							quota_request_db["quotas"][quota_title].remove(contributor)
							importcsv.db.quota_contribution_requests.replace_one({"companyid": current_user},quota_request_db)
							return {"message":"contributor rejection was created"},200
						elif quotas_rejected_exists:		
							try:
								quota_rejected_db = importcsv.db.quotas_rejected.find({"companyid": current_user})[0]
								if contributor not in quota_rejected_db[quota_title]["contributors"]:
									quota_rejected_db[quota_title]["contributors"].append(contributor)
									importcsv.db.quotas_rejected.replace_one({"companyid": current_user},quota_rejected_db)
									quota_request_db["quotas"][quota_title].remove(contributor)
									importcsv.db.quota_contribution_requests.replace_one({"companyid": current_user},quota_request_db)
									return {"message":"contributor was rejected."},200
								elif contributor in quota_rejected_db[quota_title]["contributors"]:
									return {"message":"contributor already rejected."},200
							except KeyError as kex:
								return {"error":"quota does not exist"},200


						#importcsv.db.quotas_rejected.insert_one({"companyid":current_user,quota_title:{"contributors":[contributor]}})
						#quota_request_db["quotas"][quota_title].remove(contributor)
						#importcsv.db.quota_contribution_requests.replace_one({"companyid": current_user},quota_request_db)
						#return {"message":"quota was rejected."},200

				elif contributor not in quota_request_db["quotas"][quota_title]:
					return {"message":"quota doesn't exist"},200
			elif not quota_request_exists:
				return {"message":"company doesn't exist"},200
		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"},400

	# Remove DB pending_quota_requests: {"companyid":"<hash>","userid":"<hash>","permision":"pending"}
	# Store DB accepted_quotas: {"companyid":"<hash>","userid":"<hash>","permision":"accepted"}
# Upload data to mine endpoint using multipart -> -> get response
# TODO This is done by the main contributor
@app.route('/upload_torrent_file', methods=['POST'])
@cross_origin()
def upload_torrent_file():
	direct = "CaesarTorrents"

	if request.method == 'POST':
		f = request.files['torrentfile']
		if direct in os.listdir():
			shutil.rmtree(direct)
		if direct not in os.listdir():
			os.mkdir(direct)
		buffer_filename = secure_filename(f.filename)
		f.save(os.path.join(direct, buffer_filename))

		with open(f"{direct}/{f.filename}","rb") as fb:
			data = fb.read()
		caesarfs.put(data,filename=f.filename)

		return {"message":"caesar torrent file was uploaded."}#send_from_directory(direct,f.filename) #send_file(f"{direct}/{f.filename}",as_attachment=True)
		
	# {"current_user(jwt)":"contributor","company":"","quota","","torrentfile":"<torrentfile>"}
	# Store torrent file in database
	# Coin will be generated after the torrent file has been torrented.
@app.route('/download_torrent_file', methods=['POST'])
@cross_origin()
def download_torrent_file():
	direct = "CaesarTorrentsDownload"

	if request.method == 'POST':
		torrentdetails = request.get_json()
		if direct in os.listdir():
			shutil.rmtree(direct)
		if direct not in os.listdir():
			os.mkdir(direct)
		filedata = importcsv.gridfs.fs.files.find_one({"filename":torrentdetails["torrentfile"]})
		my_id = filedata["_id"]
		output_Data = caesarfs.get(my_id).read()
		output = open(f"{direct}/{torrentdetails['torrentfile']}","wb")
		output.write(output_Data)
		output.close()
		print("download completed")

		return send_from_directory(direct,torrentdetails['torrentfile']) #send_file(f"{direct}/{f.filename}",as_attachment=True)
		
	# {"current_user(jwt)":"contributor","company":"","quota","","torrentfile":"<torrentfile>"}
	# Store torrent file in database
	# Coin will be generated after the torrent file has been torrented.
@app.route('/get_torrent', methods=['GET'])
@cross_origin()
def get_torrent():
	direct = "CaesarTorrentsDownload"

	if request.method == 'GET':
		#torrentdetails = request.get_json()
		if direct in os.listdir():
			shutil.rmtree(direct)
		if direct not in os.listdir():
			os.mkdir(direct)
		filedata = importcsv.gridfs.fs.files.find_one({"filename":"archive.zip.torrent"})
		my_id = filedata["_id"]
		output_Data = caesarfs.get(my_id).read()
		output = open(f"{direct}/archive.zip.torrent","wb")
		output.write(output_Data)
		output.close()
		print("download completed")

		return send_from_directory(direct,"archive.zip.torrent") #send_file(f"{direct}/{f.filename}",as_attachment=True)
@app.route('/get_highwaymp4_torrent', methods=['GET'])
@cross_origin()
def get_highwaymp4_torrent():
	direct = "CaesarTorrentsDownload"

	if request.method == 'GET':
		#torrentdetails = request.get_json()
		if direct in os.listdir():
			shutil.rmtree(direct)
		if direct not in os.listdir():
			os.mkdir(direct)
		filedata = importcsv.gridfs.fs.files.find_one({"filename":"highway.mp4.torrent"})
		my_id = filedata["_id"]
		output_Data = caesarfs.get(my_id).read()
		output = open(f"{direct}/highway.mp4.torrent","wb")
		output.write(output_Data)
		output.close()
		print("download completed")

		return send_from_directory(direct,"highway.mp4.torrent") #send_file(f"{direct}/{f.filename}",as_attachment=True)


@app.route('/get_highway_torrent', methods=['GET'])
@cross_origin()
def get_highway_torrent():
	direct = "CaesarTorrentsDownload"

	if request.method == 'GET':
		#torrentdetails = request.get_json()
		if direct in os.listdir():
			shutil.rmtree(direct)
		if direct not in os.listdir():
			os.mkdir(direct)
		filedata = importcsv.gridfs.fs.files.find_one({"filename":"highway.torrent"})
		my_id = filedata["_id"]
		output_Data = caesarfs.get(my_id).read()
		output = open(f"{direct}/highway.torrent","wb")
		output.write(output_Data)
		output.close()
		print("download completed")

		return send_from_directory(direct,"highway.torrent") #send_file(f"{direct}/{f.filename}",as_attachment=True)
		
	# {"current_user(jwt)":"contributor","company":"","quota","","torrentfile":"<torrentfile>"}
	# Store torrent file in database
	# Coin will be generated after the torrent file has been torrented.
    

@app.route('/chain', methods=['GET'])
@cross_origin()
def get_chain():
	try:
		chain_data = []
		if "blockchain.json" in os.listdir():
			with open("blockchain.json","r") as f:
				blockchain_file = json.load(f)
			return blockchain_file
		elif "blockchain.json" not in os.listdir():
			for ind,block in enumerate(blockchain.chain):
				chain_data.append(block.__dict__)
			return {"length": len(chain_data),"chain": chain_data}
	except Exception as ex:
		return {"error":f"{type(ex)},{ex}"}
    
    
    
@app.route('/mine_block', methods=['POST'])
@cross_origin()
def mine_block():
	try:
		minerinfo  = request.get_json()
		try:
			miner = minerinfo["miner"]
			reward = 5 #minerinfo["amount"]
		except KeyError as kex:
			return {"error":r"miner:<miner>,amount:<amount>"}
		blockchain.add_new_transaction("System",miner,reward)
		blockchain.mine()
		chain_data = []
		for block in blockchain.chain:
			chain_data.append(block.__dict__)
		blockchain_response = {"length": len(chain_data),"chain": chain_data}
		with open("blockchain.json","w+") as f:
			json.dump(blockchain_response,f)
		return json.dumps(blockchain_response)
	except Exception as ex:
		return {"error":f"{type(ex)},{ex}"}


@app.route('/make_transaction', methods=['POST'])
@cross_origin()
def make_transaction():
	try:
		senderinfo  = request.get_json()
		try:
			sender = senderinfo["sender"]
			recipient = senderinfo["recipient"]
			amount = senderinfo["amount"]
		except KeyError as kex:
			return {"error":r"sender:<sender>,recipient:<recipient>,amount:<amount>"}
		blockchain.add_new_transaction(sender,recipient,amount)
		return {"message":"transaction has been made."}
	except Exception as ex:
		return {"error":f"{type(ex)},{ex}"}

@app.route('/get_balance', methods=['POST'])
@cross_origin()
def get_balance():
	try:
		userinfo  = request.get_json()
		try:
			userbalancename = userinfo["user"]

		except KeyError as kex:
			return {"error":r"sender:<sender>,recipient:<recipient>,amount:<amount>"}
		balance = blockchain.getBalance(userbalancename)
		print(balance)
		return {"balance":{userbalancename:balance}}
	except Exception as ex:
		return {"error":f"{type(ex)},{ex}"}
# CaesarCoin Crypto wallet API's
@app.route('/get_wallet_balance', methods=['POST'])
@cross_origin()
@jwt_required()
def get_wallet_balance():
	current_user = get_jwt_identity()
	if current_user:
		try:
			user_block_details = request.get_json()
			blockchain_name_id = str(hashlib.sha256(user_block_details["blockchain_name"].encode()).hexdigest())
			try:
				blockchain_password = str(hashlib.sha256(user_block_details["blockchain_password"].encode()).hexdigest())
			except KeyError as kex:
				blockchain_password = None
			#print(current_user,blockchain_name_id,blockchain_password)
			blockchain_membership = authenticate_blockchain_membership(current_user,blockchain_name_id,blockchain_password)
			if blockchain_membership["message"] == "user is already a member of this blockchain.":
				balance = 0
				blockchain = list(importcsv.db.blockchains.find({"blockchain_name_id": blockchain_name_id}))[0]
				# This O notation is O(n^2) needs to be imporoved
				for block in blockchain["chain"]:
					if block["previous_hash"] == "" :
						#dont check the first block
						continue 
					#print(block)
					for transaction in block["transactions"]:
						if transaction["sender"] == current_user:
							balance -= transaction["amount"]
						if transaction["recipient"] == current_user:
							balance += transaction["amount"]

				return {"balance":balance}
			elif blockchain_membership["message"] == "incorrect password, not authorized to join.":
				return {"message":"incorrect password, not authorized to join."}
			else:
				return {"message":"either your not a member of the blockchain or the blockchain doesn't exist."}

		except Exception as ex:
			return {"error":f"{type(ex)},{ex}"}

# TODO Done so far
# Quota Poster creates quota with provided information
# Contributor asks permision to send data, if eligible to send data
# Then Contributor can seed torrent to contributors quota
# If the file uploaded has never been seen before for this quota coin is rewarded according to the size of the file.
# When seeding every 100 nonces of work a coin is generated which is 9 hours in real time.
# Then the quota poster looks through the catalogue of all stored magneturis
# Chooses which magneturi/file to download.
# Then starts downloading it
# TODO - Next make its slighlty more visually and user friendly then it is ready for an investor.
if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0",port=5000)
