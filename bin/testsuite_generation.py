# This file is used to generate tests from official JSON Schema Test Suite
import os
import fnmatch
import json
import test_json
import copy
import shutil

try:
    import jsonschema.validators
except ImportError:
    jsonschema = None

TESTSUITES_DIR = os.path.join(test_json.ROOT_DIR, os.path.join("JSON-Schema-Test-Suite","tests"))

TESTS_GENERATION_DIR = os.path.join(test_json.ROOT_DIR, "tests")

TYPE1 = "valid"

TYPE2 = "reflexive"

TYPE3 = "unsatisfiable"

TYPE4 = "universal"

TYPE5 = "nonvalid"

TYPE6 = "unions"

DRAFT4_ID = "draft4"

DRAFT3_ID = "draft3"

# Reading all the tests for valid type 
def cases(paths):
    with open(paths,'rb') as test_file:
        test_file = json.load(test_file)
        for test_group in test_file:
            for test in test_group["tests"]:
                test["description"] = test_group["description"] + " --> " + test["description"]
                test["schema"] = test_group["schema"]
                yield test

# Reading all the tests for nonvalid type 
def cases_not(paths):
    with open(paths,'rb') as test_file:
        test_file = json.load(test_file)
        for test_group in test_file:             
            for test in test_group["tests"]:
                if isinstance(test_group["schema"],dict):
                    ref_temp = dict_get(test_group["schema"],"$ref", None)
                    definitions_temp = dict_get(test_group["schema"],"definitions", None) 
                    defs_temp = dict_get(test_group["schema"],"$defs", None) 
                    recursiveRef_temp = dict_get(test_group["schema"],"$recursiveRef", None)
                    recursiveAnchor_temp = dict_get(test_group["schema"],"$recursiveAnchor", None)
                    # If there is a $ref in the schema, then add keyword "refRebuild" in each initial scehma
                    # This is for better processing later
                    if ref_temp == "rebuild":
                        test["refRebuild"] = "True"
                    if definitions_temp == "rebuild" or defs_temp == "rebuild":
                        test["norebuild"] = "True"
                    if recursiveRef_temp == "rebuild":
                        test["recurRebuild"] = "True"
                    if recursiveAnchor_temp == "recursiveAnchorrebuild":
                        test["recursiveAnchor"] = "True"    
                    if recursiveAnchor_temp == "rebuild":
                        test["AnchorFalse"] = "True"
                    test["schema"] = test_group["schema"]
                    test["description"] = test_group["description"] + " --> " + test["description"]
                    yield test
                else:
                    test["description"] = test_group["description"] + " --> " + test["description"]
                    test["schema"] = test_group["schema"]
                    yield test

# Reading all the tests for universal, unsatisfiable and reflexity type                         
def cases_not_in_tests(paths, draft):
    with open(paths,'rb') as test_file:
        test_file = json.load(test_file)
        if draft == DRAFT4_ID:
            id_key = "id"
        else:
            id_key = "$id"
        for test_group in test_file:
            if isinstance(test_group["schema"],dict):
                ref_temp = dict_get(test_group["schema"],"$ref", None)
                id_temp = dict_get(test_group["schema"],id_key, None)
                anchor_temp = dict_get(test_group["schema"],"$anchor", None)     
                recursiveRef_temp = dict_get(test_group["schema"],"$recursiveRef", None) 
                dynamicRef_temp = dict_get(test_group["schema"],"$dynamicRef", None)  
                dynamicAnchor_temp = dict_get(test_group["schema"],"$dynamicAnchor", None)  
                recursiveAnchor_temp = dict_get(test_group["schema"],"$recursiveAnchor", None)
                definitions_temp = dict_get(test_group["schema"],"definitions", None) 
                defs_temp = dict_get(test_group["schema"],"$defs", None) 
                if ref_temp == "rebuild":
                    test_group["refRebuild"] = "True"
                if id_temp == "rebuild":
                    test_group["Rebuild"] = "True"
                if anchor_temp == "rebuild":
                    test_group["Rebuild"] = "True"
                if recursiveRef_temp == "rebuild":
                    test_group["recurRebuild"] = "True"
                if dynamicRef_temp == "rebuild":
                    test_group["Rebuild"] = "True"
                if dynamicAnchor_temp == "rebuild":
                    test_group["Rebuild"] = "True"
                if recursiveAnchor_temp == "recursiveAnchorrebuild":
                    test_group["recursiveAnchor"] = "True"    
                if recursiveAnchor_temp == "rebuild":
                    test_group["AnchorFalse"] = "True" 
                if definitions_temp == "rebuild" or defs_temp == "rebuild":
                    test_group["norebuild"] = "True"            
                yield test_group
            else:
                yield test_group

# Reading all the tests for unions type   
def cases_union_tests(paths):
    with open(paths,'rb') as test_file:
        test_file = json.load(test_file)     
        for test_group in test_file:
            test_group["testsUnion"] = []
            test_group["testsUnionValid"] = []
            for test in test_group["tests"]:
                if test["valid"] == True:
                    testDic = {}
                    testDic["const"] = test["data"]
                    test_group["testsUnion"].append(testDic)
            yield test_group

# Go through the schema recursively, if there is the keyword we are searching, return the specific result 
def dict_get(diction, objkey, default):
    tmp = diction
    for k,v in tmp.items():
        if k == objkey:
            default = "rebuild"
            if objkey == "$recursiveAnchor" and tmp[k] == True:
                default = "recursiveAnchorrebuild"
            if isinstance(v,dict):
                ret = dict_get(v, objkey, default)
                if ret is not default:
                    return ret
        elif k != objkey and isinstance(v,dict):
            ret = dict_get(v, objkey, default)
            if ret is not default:
                return ret
        elif k != objkey and isinstance(v,list):
            for item in v:
                if isinstance(item,dict):
                    ret = dict_get(item, objkey, default)
                    if ret is not default:
                        return ret
    return default

# Path correction for $ref and $recursiveRef
def dict_rebuild_only_ref(diction, objkey, jionType, notOr, position, type, ref_recur_anchor):
    tmp = diction
    for k,v in tmp.items():
        if k == objkey:
            ref_anchor = str(v).startswith("#/")
            if(ref_recur_anchor == True):
                ref_anchor = str(v).startswith("#/") and not str(v).startswith("#/$defs")
            if ref_anchor:
                original = str(v)[2:(len(str(v)))]
                if notOr != "":
                    notOr = notOr + "/"
                if jionType != "":
                    jionType = jionType + "/"
                if position != "":
                    position = position + "/"
                tmp[k] = "#/" + jionType + position + notOr + original
                return tmp
            elif str(v) == "#":
                if type == "true_schemas" or type == "false_schemas":
                    if notOr != "":
                        notOr =  "/" + notOr
                if jionType != "":
                    jionType = jionType + "/"
                tmp[k] = "#/" + jionType + position +  notOr 
                return tmp
            elif isinstance(v,dict):
                dict_rebuild_only_ref(v, objkey, jionType, notOr, position, type, ref_recur_anchor)
        elif k != objkey and isinstance(v,dict):
            dict_rebuild_only_ref(v, objkey, jionType, notOr, position, type, ref_recur_anchor)
        elif k != objkey and isinstance(v,list):
            for item in v:
                if isinstance(item,dict):
                    dict_rebuild_only_ref(item, objkey, jionType, notOr, position, type, ref_recur_anchor)
    return tmp

# Rename for $ref， $anchor，$dynamicAnchor， $dynamicRef， $recursiveRef
def dict_rebuild_add_at_tail(diction, objkey):
    tmp = diction
    for k,v in tmp.items():
        if k == objkey and objkey == "$anchor":
            tmp[k] = str(v) + "1"
        elif k == objkey and (objkey == "id"  or objkey == "$id"):
            index_json = str(v).find(".json")
            if index_json > 0:
                tmp[k] = str(v)[0:(index_json)] + "1" + str(v)[index_json:(len(str(v)))]             
            else:
                tmp[k] = str(v) + "1"           
        elif k == objkey and objkey == "$ref":
            index_hashtag = str(v).find("#")
            index_json2 = str(v).find(".json")
            if str(v).startswith("http"):
                if index_hashtag > 0 and index_json2 > 0 and index_hashtag > index_json2:
                    part1 = str(v)[0:(index_json2)]
                    part2 = str(v)[index_json2:(len(str(v)))]
                    tmp[k] = part1 + "1" + part2 + "1"
                elif index_hashtag < 0 and index_json2 > 0:
                    tmp[k] = str(v)[0:(index_json2)] + "1" + str(v)[index_json2:(len(str(v)))]
                elif index_hashtag > 0 and index_json2 < 0:
                    part1 = str(v)[0:(index_hashtag)]
                    part2 = str(v)[index_hashtag:(len(str(v)))]
                    if part2 == "#":
                        continue 
                    else:
                        tmp[k] = part1 + "1" + part2 + "1"
            elif not str(v).startswith("http") and not str(v).startswith("#/") and str(v) != "#" and index_hashtag > 0 and index_json2 > 0:
                part1 = str(v)[0:(index_json2)]
                part2 = str(v)[index_json2:(len(str(v)))]
                tmp[k] = part1 + "1" + part2
            elif not str(v).startswith("http") and not str(v).startswith("#/") and str(v) != "#" and not isinstance(v,dict) and index_hashtag < 0:
                tmp[k] = str(v) + "1"
            elif not str(v).startswith("http") and not str(v).startswith("#/") and str(v) != "#" and not isinstance(v,dict) and str(v).startswith("#"):
                tmp[k] = str(v) + "1"
        elif k == objkey and objkey == "$dynamicRef" :
            index_hashtag2 = str(v).find("#")
            if str(v).startswith("#"):
                tmp[k] = str(v) + "1"
            elif not str(v).startswith("#") and index_hashtag2 > 0:
                tmp[k] = str(v)[0:(index_hashtag2)] + "1" + str(v)[index_hashtag2:(len(str(v)))] + "1"
        elif k == objkey and objkey == "$dynamicAnchor":
            tmp[k] = str(v) + "1"
        elif k != objkey and isinstance(v,dict):
            dict_rebuild_add_at_tail(v, objkey)
        elif k != objkey and isinstance(v,list):
            for item in v:
                if isinstance(item,dict):
                    dict_rebuild_add_at_tail(item, objkey)
    return tmp

# Special generation for definitions or $defs
def dict_definition_rebuild(schema):
    key_len = len(schema.keys())
    for k,v in schema.items():
        if k != "definitions" and k != "$defs" and (k == "$ref" or key_len == 2):
            temp_key = k
            temp_dict = {k:v}              
            schema["not"] = temp_dict
            schema.pop(temp_key)
            return schema
        elif k == "if":
            temp = {}
            temp["if"] = v
            if "then" in schema.keys():
                temp["then"] = schema["then"]
            if "else" in schema.keys():
                temp["else"] = schema["else"]
            schema["not"] = temp
            schema.pop("if")
            if "then" in schema.keys():
                schema.pop("then")
            if "else" in schema.keys():
                schema.pop("else")
            return schema
        elif isinstance(v,dict):
            if dict_get(v, "$ref", None) == "rebuild" and k != "definitions" and k != "$defs":
                temp_key = k
                temp_dict = {k:v}              
                schema["not"] = temp_dict
                schema.pop(temp_key)
                return schema               
            elif not dict_get(v, "$ref", None) == "rebuild" and k != "definitions" and k != "$defs" and key_len == 2:
                temp_key = k
                temp_dict = {k:v}              
                schema["not"] = temp_dict
                schema.pop(temp_key)
                return schema             
        elif isinstance(v,list):
            for item in v:
                if isinstance(item,dict):
                    for key,value in item.items():
                        if key == "$ref" or (isinstance(value,dict) and dict_get(value, "$ref", None) == "rebuild"):
                            temp_key = k
                            temp_dict = {k:v}              
                            schema["not"] = temp_dict
                            schema.pop(temp_key)  
                            return schema
    return schema

# Logical process to deal with all the tests
def rebuild(case_schema, schema_type, case, draft, jionType, notOr, position, type):
    if draft == DRAFT4_ID:
        id_key = "id"
    else:
        id_key = "$id"
    test_schema = case["schema"]
    recur_ref_works = False
    ref_recur_anchor = False
    if "recurRebuild" in case.keys() and "recursiveAnchor" in case.keys():
        recur_ref_works = True
    if "refRebuild" in case.keys() and ("recursiveAnchor" in case.keys() or "AnchorFalse" in case.keys()):
        ref_recur_anchor = True
    if schema_type == "1" and "norebuild" in case.keys():
        test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
        if recur_ref_works == False:
            test_schema = dict_rebuild_only_ref(case_schema, "$recursiveRef", jionType, notOr, position, type, ref_recur_anchor)
    elif schema_type == "1" and recur_ref_works == False and "norebuild" not in case.keys():     
        test_schema = dict_rebuild_only_ref(case_schema, "$recursiveRef", jionType, notOr, position, type, ref_recur_anchor)
        if "refRebuild" in case.keys():
            test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
    elif schema_type == "1" and recur_ref_works == True and "refRebuild" in case.keys() and "norebuild" not in case.keys():
        test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
    elif schema_type == "2" and "norebuild" in case.keys():
        test_schema = dict_definition_rebuild(case_schema)
        test_schema = dict_rebuild_add_at_tail(case_schema,"$ref")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$anchor")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicAnchor") 
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicRef")       
        test_schema = dict_rebuild_add_at_tail(case_schema,id_key)
        test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
        if recur_ref_works == False:
            test_schema = dict_rebuild_only_ref(case_schema, "$recursiveRef", jionType, notOr, position, type, ref_recur_anchor)
    elif schema_type == "2" and "Rebuild" in case.keys():
        test_schema = dict_rebuild_add_at_tail(case_schema,"$ref")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$anchor")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicAnchor") 
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicRef")       
        test_schema = dict_rebuild_add_at_tail(case_schema,id_key)
        test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
        if recur_ref_works == False:
            test_schema = dict_rebuild_only_ref(case_schema, "$recursiveRef", jionType, notOr, position, type, ref_recur_anchor)
    elif schema_type == "2" and "refRebuild" in case.keys() :
        test_schema = dict_rebuild_add_at_tail(case_schema,"$ref")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$anchor")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicAnchor") 
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicRef")       
        test_schema = dict_rebuild_add_at_tail(case_schema,id_key)
        test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
        if recur_ref_works == False:
            test_schema = dict_rebuild_only_ref(case_schema, "$recursiveRef", jionType, notOr, position, type, ref_recur_anchor)
    elif schema_type == "2" and "recurRebuild" in case.keys():
        test_schema = dict_rebuild_add_at_tail(case_schema,"$ref")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$anchor")
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicAnchor") 
        test_schema = dict_rebuild_add_at_tail(case_schema,"$dynamicRef")       
        test_schema = dict_rebuild_add_at_tail(case_schema,id_key)
        test_schema = dict_rebuild_only_ref(case_schema, "$ref", jionType, notOr, position, type, ref_recur_anchor)
        if recur_ref_works == False:
            test_schema = dict_rebuild_only_ref(case_schema, "$recursiveRef", jionType, notOr, position, type, ref_recur_anchor)
    return test_schema

def generate_valid_schemas(old_path,new_path, draft):
    tests_generate_path = os.path.join(new_path,TYPE1)
    if  not os.path.exists(tests_generate_path):
        os.makedirs(tests_generate_path)
    recursive_create_testsuites(old_path,tests_generate_path,TYPE1, draft)

def generate_reflexivity(old_path,new_path, draft):
    tests_generate_path = os.path.join(new_path,TYPE2)
    if  not os.path.exists(tests_generate_path):
        os.makedirs(tests_generate_path)
    recursive_create_testsuites(old_path,tests_generate_path,TYPE2, draft)

def generate_false_schemas(old_path,new_path, draft):
    tests_generate_path = os.path.join(new_path,TYPE3)
    if  not os.path.exists(tests_generate_path):
        os.makedirs(tests_generate_path)
    recursive_create_testsuites(old_path,tests_generate_path,TYPE3, draft)

def generate_true_schemas(old_path,new_path, draft):
    tests_generate_path = os.path.join(new_path,TYPE4)
    if  not os.path.exists(tests_generate_path):
        os.makedirs(tests_generate_path)
    recursive_create_testsuites(old_path,tests_generate_path,TYPE4, draft)

def generate_invalid_witnesses(old_path,new_path, draft):
    tests_generate_path = os.path.join(new_path,TYPE5)
    if  not os.path.exists(tests_generate_path):
        os.makedirs(tests_generate_path)
    recursive_create_testsuites(old_path,tests_generate_path,TYPE5, draft)

def generate_union_schemas(old_path,new_path, draft):
    tests_generate_path = os.path.join(new_path,TYPE6)
    if  not os.path.exists(tests_generate_path):
        os.makedirs(tests_generate_path)
    recursive_create_testsuites(old_path,tests_generate_path,TYPE6, draft)

def read_and_write_valid_schemas(old_path,new_path,file_name, draft):
    msg = []
    count = 1
    for case in cases(old_path):
        test_data = case["data"]
        test_valid = case["valid"]
        test_schema = case["schema"]
        testcase = {
            "id": count,
            "schema1": {
                "const": test_data
            },
            "schema2": test_schema,
            "tests": {
                "s1SubsetEqOfs2": test_valid
            }
        }
        msg.append(testcase)
        count += 1
    with open(new_path,"w") as f:        
        json.dump(msg, f, indent = 4)

def read_and_write_reflexivity(old_path,new_path,file_name, draft):
    msg = []
    count = 1
    for case in cases_not_in_tests(old_path, draft):
        test_schema = case["schema"]
        testcase = {
            "id": count,
            "schema1": test_schema,
            "schema2": test_schema,
            "tests": {
                "s1SubsetEqOfs2": True,
                "s2SubsetEqOfs1": True
            }
        }
        msg.append(testcase)
        count += 1
    with open(new_path,"w") as f:        
        json.dump(msg, f, indent = 4)

def read_and_write_false_schemas(old_path,new_path,file_name, draft):
    msg = []
    count = 1
    for case in cases_not_in_tests(old_path, draft): 
        if not isinstance(case["schema"],bool) and "norebuild" not in case.keys():
            case1 = copy.deepcopy(case["schema"])
            case2 = copy.deepcopy(case["schema"])
            test_schema1 = rebuild(case1,"1", case, draft, "allOf","","0","false_schemas")
            test_schema21 = rebuild(case2,"2",case, draft, "allOf","not","1","false_schemas")
            test_schema2 = {
                        "not": test_schema21
                    }
        elif not isinstance(case["schema"],bool) and "norebuild" in case.keys():
            case1 = copy.deepcopy(case["schema"])
            case2 = copy.deepcopy(case["schema"])
            test_schema1 = rebuild(case1,"1", case, draft, "allOf","","0","false_schemas")
            test_schema2 = rebuild(case2,"2",case, draft, "allOf","","1","false_schemas")
        else:
            test_schema1 = case["schema"]
            test_schema2 = {
                "not":case["schema"]
            }

        if draft == DRAFT3_ID or draft == DRAFT4_ID:
            schema2 = {
                "not": {}
            }
        else:
            schema2 = False
        
        testcase = {
            "id": count,
            "schema1": {
                "allOf": [
                    test_schema1,
                    test_schema2
                ]
            },
            "schema2": schema2,
            "tests": {
                "s1SubsetEqOfs2": True,
                "s2SubsetEqOfs1": True
            }
        }
        if len(msg) > 0 and msg[len(msg)-1]["schema1"] == testcase["schema1"]:
                continue                             
        else:
            msg.append(testcase)
            count += 1
    if msg:
        with open(new_path,"w") as f:        
            json.dump(msg, f, indent = 4)

def read_and_write_true_schemas(old_path,new_path,file_name, draft):
    msg = []
    count = 1
    for case in cases_not_in_tests(old_path, draft):
        if not isinstance(case["schema"],bool) and "norebuild" not in case.keys():
            case1 = copy.deepcopy(case["schema"])
            case2 = copy.deepcopy(case["schema"])
            test_schema1 = rebuild(case1,"1", case, draft, "anyOf","","0","true_schemas")
            test_schema21 = rebuild(case2,"2",case, draft, "anyOf","not","1","true_schemas")
            test_schema2 = {
                        "not": test_schema21
                    }
        elif not isinstance(case["schema"],bool) and "norebuild" in case.keys():
            case1 = copy.deepcopy(case["schema"])
            case2 = copy.deepcopy(case["schema"])
            test_schema1 = rebuild(case1,"1", case, draft, "anyOf","","0","true_schemas")
            test_schema2 = rebuild(case2,"2",case, draft, "anyOf","","1","true_schemas")
        else:
            test_schema1 = case["schema"]
            test_schema2 = {
                "not":case["schema"]
            }

        if draft == DRAFT3_ID or draft == DRAFT4_ID:
            schema2 = {
            }
        else:
            schema2 = True
        testcase = {
            "id": count,
            "schema1": {
                "anyOf": [
                    test_schema1,
                    test_schema2
                ]
            },
            "schema2": schema2,
            "tests": {
                "s1SubsetEqOfs2": True,
                "s2SubsetEqOfs1": True
            }
        }
        if len(msg) > 0 and msg[len(msg)-1]["schema1"] == testcase["schema1"]:
                continue                             
        else:
            msg.append(testcase)
            count += 1

    if msg:
        with open(new_path,"w") as f:        
            json.dump(msg, f, indent = 4)

def read_and_write_invalid_witnesses(old_path,new_path,file_name, draft):
    msg = []
    count = 1
    for case in cases_not(old_path):
        case1 = copy.deepcopy(case["schema"])
        ref_recur_anchor = False
        recur_ref_works = False
        if "recurRebuild" in case.keys() and "recursiveAnchor" in case.keys():
            recur_ref_works = True
        if "refRebuild" in case.keys() and ("recursiveAnchor" in case.keys() or "AnchorFalse" in case.keys()):
            ref_recur_anchor = True
        if "norebuild" in case.keys():
            test_schema = dict_definition_rebuild(case1)
        elif "norebuild" not in case.keys():  
            test_schema1 = case1
            if "refRebuild" in case.keys():
                test_schema1 = dict_rebuild_only_ref(case1,"$ref", "","not","","invalid_witnesses", ref_recur_anchor)   
            if "recurRebuild" in case.keys() and recur_ref_works == False:
                test_schema1 = dict_rebuild_only_ref(case1, "$recursiveRef", "", "not", "", "invalid_witnesses", ref_recur_anchor)         
            test_schema = {
                "not": test_schema1
            } 
        else:
            test_schema = {
                "not": case["schema"]
            }
            
        test_data = case["data"]
        test_valid = case["valid"]
        if test_valid == True:
            testcase = {
                "id": count,
                "schema1": {
                    "const": test_data
                },
                "schema2": test_schema,
                "tests": {
                    "s1SubsetEqOfs2": False
                }
            }
            msg.append(testcase)
            count += 1
    if msg:    
        with open(new_path,"w") as f:        
            json.dump(msg, f, indent = 4)

def read_and_write_union_schemas(old_path,new_path,file_name, draft):
    msg = []
    count = 1
    for case in cases_union_tests(old_path):
        if len(case["testsUnion"]) >= 2:
            test_schema = case["schema"]
            test_union = case["testsUnion"]
            testcase = {
                "id": count,
                "schema1": {
                    "anyOf": test_union
                    
                },
                "schema2": test_schema,
                "tests": {
                    "s1SubsetEqOfs2": True
                }
            }
            msg.append(testcase)
            count += 1
    if msg:
        with open(new_path,"w") as f:        
            json.dump(msg, f, indent = 4)

# old_path: templates from JSON-Schema-Test-Suite
# new_path: the path we need to generate our new test suite regarding to JSON-Schema-Test-Suite
def recursive_create_testsuites(old_path,new_path,testsuites_type, draft):
    for folder in os.listdir(old_path):
        folder_path_branch = os.path.join(old_path, folder)
        # Create folders recursively
        if os.path.isdir(folder_path_branch) and folder is not None:
            new_folder_path_branch = os.path.join(new_path, folder)
            if os.path.exists(new_folder_path_branch):
                # file or folder exist
                shutil.rmtree(new_folder_path_branch)
            os.makedirs(new_folder_path_branch)
            recursive_create_testsuites(folder_path_branch,new_folder_path_branch,testsuites_type, draft)
        # If in the old_path is json files, then take it as a template to generate our new test suite
        elif folder.endswith(".json"):
            new_file_path = os.path.join(new_path, folder)
            # Write test case from JSON-Schema-Test-Suite
            if testsuites_type == TYPE1 and folder != "refRemote.json":
                read_and_write_valid_schemas(folder_path_branch, new_file_path, folder, draft)
            if testsuites_type == TYPE2 and folder != "refRemote.json":
                read_and_write_reflexivity(folder_path_branch, new_file_path, folder, draft)
            if testsuites_type == TYPE3 and folder != "refRemote.json":
                read_and_write_false_schemas(folder_path_branch, new_file_path, folder, draft)
            if testsuites_type == TYPE4 and folder != "refRemote.json":
                read_and_write_true_schemas(folder_path_branch, new_file_path, folder, draft)     
            if testsuites_type == TYPE5 and folder != "refRemote.json":
                read_and_write_invalid_witnesses(folder_path_branch, new_file_path, folder, draft)
            if testsuites_type == TYPE6 and folder != "refRemote.json":
                read_and_write_union_schemas(folder_path_branch, new_file_path, folder, draft)
        else: 
            print(folder_path_branch," can ignore, because there is no json file.")

def create_new_folders(path):
    for draft in os.listdir(path):
        print(draft)
        draft_path = os.path.join(path, draft)
        if os.path.isdir(draft_path) and draft is not None:
            # Create new draft folder in our own tests
            new_draft_path = os.path.join(TESTS_GENERATION_DIR, draft)
            # All test suites generated from JSON-Schema-Test-Suite are under this folder
            generate_valid_schemas(draft_path,new_draft_path, draft)
            generate_reflexivity(draft_path,new_draft_path, draft)
            generate_false_schemas(draft_path,new_draft_path, draft)
            generate_true_schemas(draft_path,new_draft_path, draft)
            generate_invalid_witnesses(draft_path,new_draft_path, draft)
            generate_union_schemas(draft_path,new_draft_path, draft)
        else:
            print(draft_path," can ignore, because there is no json file or json files in here do not belong to any draft.")


def read_testsuites():
    # Looking for testsuites in "JSON-Schema-Test-Suite"
    print("Looking for JSON-Schema-Test-Suite in %s" % TESTSUITES_DIR)
    create_new_folders(TESTSUITES_DIR)

if __name__ == "__main__":
    read_testsuites()