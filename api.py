from flask import Flask,request,jsonify
from flask_restful import Resource,Api,reqparse
import json
import pymongo
from json_metadata_validator import JsonMetadataValidator
from numpy import require

app = Flask(__name__)
api=Api(app)


class PrintingDyeType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["printing_dye"].find({}, {"_id" : 0})]
        
        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(PrintingDyeType, "/v0/stvgodigital/pps3/techpack/info/printing")


# Endpoint which returns the info about the POMs
# of a single garment 
# @params: type of garment
class InfoPOM(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("garmentType", required = True, location = "json")
    
    def get(self):
        args = self.parser_get.parse_args()

        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        query = [
            {
                "$lookup" : {
                    "from" : "pom_part",
                    "localField" : "partCode",
                    "foreignField" : "code",
                    "as" : "part"
                }
            },

            {
                "$unwind" : "$part"
            },
            
            {
                "$group" : {
                    "_id" : {
                        "partCode" : "$partCode",
                        "sectionCode" : "$sectionCode",
                        "part" : "$part"
                    },
                    "points" : {
                        "$push" : "$$ROOT"
                    }
                }
            },

            {
                "$group" : {
                    "_id" : {
                          "partCode" : "$_id.partCode",
                           "part" : "$_id.part"
                    },
                    "sections" : {
                        "$push" : {
                            "sectionCode" : "$_id.sectionCode",
                            "points" : "$points"
                        }
                    }
                }
            },

            {
                "$project" : {
                    "part" : "$_id.part",
                    "sections" : 1
                }
            },

            {
                "$project" : {
                    "_id" : 0,
                    "sections.points._id" : 0,
                    "sections.points.sectionCode" : 0,
                    "sections.points.partCode" : 0,
                    "sections.points.part" : 0,
                    "part._id" : 0
                }
            },

            {
                "$unwind" : "$sections"
            },

            {
                "$lookup" : {
                    "from" : "pom_section",
                    "let" : {
                        "section" : "$sections.sectionCode",
                        "part" : "$part.code"
                    },
                    "pipeline" : [
                        {
                            "$match" : {
                                "$expr": {
                                    "$and" : [
                                        {
                                            "$eq" : ["$code", "$$section"]
                                        },
                                        {
                                            "$eq" : ["$partCode", "$$part"]
                                        }
                                    ]
                                }
                            }
                        }
                    ],
                    "as" : "section"
                }
            },

            {
                "$unwind" : "$section"
            },

            {
                "$project" : {
                    "part" : 1,
                    "sections.section" : "$section",
                    "sections.points" : 1,
                }
            },

            {
                "$project" : {
                    "sections.section._id" : 0
                }
            },

            {
                "$match" : {
                    "sections.section.garmentType" : {
                        "$eq" : args["garmentType"]
                    }
                }
            },

            {
                "$group" : {
                    "_id" : {
                        "partCode" : "$part.code",
                        "part" : "$part"
                    },
                    "sections" : {
                        "$push" : "$sections"
                    }
                }
            },

            {
                "$project" : {
                    "part" : "$_id.part",
                    "sections" : 1
                }
            },

            {
                "$project" : {
                    "_id" : 0,
                    "sections.section.garmentType" : 0,
                    "sections.section.partCode" : 0
                }
            }
        ]

        data = [r for r in database["techpack"]["pom_point"].aggregate(query)]

        if data == []:
            response = jsonify({"message" : "Invalid garmentType."})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response
        

api.add_resource(InfoPOM, "/v0/stvgodigital/pps3/techpack/info/pom")

# Endpoint which returns the info about the garments
# supported by the API
class InfoGarment(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["garment_type"].find({}, {"_id": 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(InfoGarment, "/v0/stvgodigital/pps3/techpack/info/garment")


class InfoSeason(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["season"].find({}, {"_id" : 0})]
        
        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(InfoSeason, "/v0/stvgodigital/pps3/techpack/info/season")


class InfoSex(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["sex"].find({}, {"_id" : 0})]
        
        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(InfoSex, "/v0/stvgodigital/pps3/techpack/info/sex")


class InfoFit(Resource):
    def get(self):
        database = pymongo.MongoClient(port=27017, username = "root", password = "password")
        
        data = [d for d in database["techpack"]["fit"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(InfoFit, "/v0/stvgodigital/pps3/techpack/info/fit")


class InfoClassification(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["classification"].find({}, {"_id" : 0})]
        
        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(InfoClassification, "/v0/stvgodigital/pps3/techpack/info/classification")


class InfoComposition(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["composition"].find({}, {"_id" : 0})]
        
        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(InfoComposition, "/v0/stvgodigital/pps3/techpack/info/composition")


class InfoCareInstruction(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("careType", required = False, location = "json", type = str)

    def get(self):
        args = self.parser_get.parse_args()
      
        if args["careType"] is not None:
            database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

            data = [ d for d in database["techpack"]["care_instruction"].find({"careType" : args["careType"]}, {"_id" : 0})]

            if data != []:              
                response = jsonify(data)
                response.status_code = 200

            else:
                response = jsonify({"message" : "The specified type is not allowed!"})
                response.status_code = 406

        else:
            database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

            data = [d for d in database["techpack"]["care_instruction"].find({}, {"_id" : 0})]

            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(InfoCareInstruction, "/v0/stvgodigital/pps3/techpack/info/careinstruction")


class BomType(Resource):
    #parser_get = reqparse.RequestParser()
    #parser_get.add_argument("")

    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")
        
        data = [d for d in database["techpack"]["bom_type"].find({}, {"_id" : 0, "metadata" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(BomType, "/v0/stvgodigital/pps3/techpack/info/bom")


class BomTypeMetadata(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("bomType", required = True, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")
        
        result = database["techpack"]["bom_type"].aggregate(
            [
                {
                    "$match" : {
                        "code" : args["bomType"]
                    }
                },

                {
                    "$lookup" : {
                        "from" : "metadata",
                        "localField" : "metadata",
                        "foreignField" : "type",
                        "as" : "metadataType"
                    }
                },

                {
                    "$unwind" : "$metadataType"
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "metadataType.metadata" : 1
                    }
                }
            ]
        )

        data = None

        for r in result:
            data = r["metadataType"]["metadata"]

        if data is None:
            response = jsonify({"message" : "The bomType provided is not valid!"})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(BomTypeMetadata, "/v0/stvgodigital/pps3/techpack/info/bom/metadata")


class ButtonholeType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["buttonhole_type"].find({}, {"_id" : 0, "metadata" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(ButtonholeType, "/v0/stvgodigital/pps3/techpack/info/buttonhole")


class ButtonType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["button_stitching"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(ButtonType, "/v0/stvgodigital/pps3/techpack/info/button")


class FabricType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["fabric"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(FabricType, "/v0/stvgodigital/pps3/techpack/info/fabric")


class GarmentSide(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["garment_side"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(GarmentSide, "/v0/stvgodigital/pps3/techpack/info/side")


class Orientation(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["orientation"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(Orientation, "/v0/stvgodigital/pps3/techpack/info/orientation")


class LabelStitching(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["label_stitching"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(LabelStitching, "/v0/stvgodigital/pps3/techpack/info/label/stitching")


class SeamInfo(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("seamClass", required = False, location = "json")
    parser_get.add_argument("seamSubclass", required = False, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        if args["seamClass"] is None and args["seamSubclass"] is None:
            query = [
                {
                    "$lookup" : {
                        "from" : "sewing_subclass",
                        "localField" : "subClassCode",
                        "foreignField" : "code",
                        "as" : "sewingSubclass"
                    }
                },

                {
                    "$unwind" : "$sewingSubclass"
                },

                {
                    "$group" : {
                        "_id" : {
                            "code" : "$subClassCode",
                            "sewingSubClass" : "$sewingSubclass"
                        },
                        "options" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$project" : {
                        "sewingSubClass" : "$_id.sewingSubClass",
                        "options" : 1
                    }
                },
                
                {
                    "$project" : {
                        "sewingSubClass._id" : 0,
                        "_id" : 0,
                        "options._id" : 0,
                        "options.subClassCode" : 0,
                        "options.sewingSubclass" : 0
                    }
                },

                {
                    "$lookup" : {
                        "from" : "sewing_class",
                        "localField" : "sewingSubClass.classCode",
                        "foreignField" : "code",
                        "as" : "sewingClass"
                    }
                },

                {
                    "$unwind" : "$sewingClass"
                },

                {
                    "$group" : {
                        "_id" : {
                            "code" : "$sewingClass.code",
                            "sewingClass" : "$sewingClass"
                        },
                        "sewingSubClasses" : {
                            "$push" : {
                                "sewingSubClass" : "$sewingSubClass",
                                "options" : "$options"
                            }
                        }
                    }
                },

                {
                    "$project" : {
                        "sewingClass" : "$_id.sewingClass",
                        "sewingSubClasses" : 1
                    }
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "sewingSubClasses.sewingSubClass.classCode" : 0,
                        "sewingClass._id" : 0
                    }
                }
            ]

        elif args["seamSubclass"] is not None:
            query = [
                {
                    "$lookup" : {
                        "from" : "sewing_subclass",
                        "localField" : "subClassCode",
                        "foreignField" : "code",
                        "as" : "sewingSubclass"
                    }
                },

                {
                    "$unwind" : "$sewingSubclass"
                },

                {
                    "$match" : {
                        "sewingSubclass.code" : args["seamSubclass"] 
                    }
                },

                {
                    "$group" : {
                        "_id" : {
                            "code" : "$subClassCode",
                            "sewingSubClass" : "$sewingSubclass"
                        },
                        "options" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$project" : {
                        "sewingSubClass" : "$_id.sewingSubClass",
                        "options" : 1
                    }
                },
                
                {
                    "$project" : {
                        "sewingSubClass._id" : 0,
                        "_id" : 0,
                        "options._id" : 0,
                        "options.subClassCode" : 0,
                        "options.sewingSubclass" : 0
                    }
                },

                {
                    "$lookup" : {
                        "from" : "sewing_class",
                        "localField" : "sewingSubClass.classCode",
                        "foreignField" : "code",
                        "as" : "sewingClass"
                    }
                },

                {
                    "$unwind" : "$sewingClass"
                },

                {
                    "$group" : {
                        "_id" : {
                            "code" : "$sewingClass.code",
                            "sewingClass" : "$sewingClass"
                        },
                        "sewingSubClasses" : {
                            "$push" : {
                                "sewingSubClass" : "$sewingSubClass",
                                "options" : "$options"
                            }
                        }
                    }
                },

                {
                    "$project" : {
                        "sewingClass" : "$_id.sewingClass",
                        "sewingSubClasses" : 1
                    }
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "sewingSubClasses.sewingSubClass.classCode" : 0,
                        "sewingClass._id" : 0
                    }
                }
            ]

        elif args["seamClass"] is not None:
            query = [
                {
                    "$lookup" : {
                        "from" : "sewing_subclass",
                        "localField" : "subClassCode",
                        "foreignField" : "code",
                        "as" : "sewingSubclass"
                    }
                },

                {
                    "$unwind" : "$sewingSubclass"
                },

                {
                    "$group" : {
                        "_id" : {
                            "code" : "$subClassCode",
                            "sewingSubClass" : "$sewingSubclass"
                        },
                        "options" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$project" : {
                        "sewingSubClass" : "$_id.sewingSubClass",
                        "options" : 1
                    }
                },
                
                {
                    "$project" : {
                        "sewingSubClass._id" : 0,
                        "_id" : 0,
                        "options._id" : 0,
                        "options.subClassCode" : 0,
                        "options.sewingSubclass" : 0
                    }
                },

                {
                    "$lookup" : {
                        "from" : "sewing_class",
                        "localField" : "sewingSubClass.classCode",
                        "foreignField" : "code",
                        "as" : "sewingClass"
                    }
                },

                {
                    "$unwind" : "$sewingClass"
                },

                {
                    "$match" : {
                        "sewingClass.code" : args["seamClass"]
                    }
                },

                {
                    "$group" : {
                        "_id" : {
                            "code" : "$sewingClass.code",
                            "sewingClass" : "$sewingClass"
                        },
                        "sewingSubClasses" : {
                            "$push" : {
                                "sewingSubClass" : "$sewingSubClass",
                                "options" : "$options"
                            }
                        }
                    }
                },

                {
                    "$project" : {
                        "sewingClass" : "$_id.sewingClass",
                        "sewingSubClasses" : 1
                    }
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "sewingSubClasses.sewingSubClass.classCode" : 0,
                        "sewingClass._id" : 0
                    }
                }
            ]

        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["sewing_option"].aggregate(query)]

        if data == []:
            response = jsonify({"message" : "Invalid arguments."})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(SeamInfo, "/v0/stvgodigital/pps3/techpack/info/sewing/seam")

class LabelType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["label_type"].find({}, {"_id" : 0, "metadata" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(LabelType, "/v0/stvgodigital/pps3/techpack/info/label/type")

class StitchInfo(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("stitchClass", required = False, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        if args["stitchClass"] is None:
            query = [
                {
                    "$group" : {
                        "_id" : "$class",
                        "options" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$lookup" : {
                        "from" : "stitch_class",
                        "localField" : "_id",
                        "foreignField" : "code",
                        "as" : "stitchClass"
                    }
                },

                {
                    "$unwind" : "$stitchClass"
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "options.class" : 0,
                        "options._id" : 0,
                        "stitchClass._id" : 0
                    }
                }
            ]
        
        else:
            query = [
                {
                    "$match" : {
                        "class" : args["stitchClass"]
                    }
                },
                
                {
                    "$group" : {
                        "_id" : "$class",
                        "options" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$lookup" : {
                        "from" : "stitch_class",
                        "localField" : "_id",
                        "foreignField" : "code",
                        "as" : "stitchClass"
                    }
                },

                {
                    "$unwind" : "$stitchClass"
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "options.class" : 0,
                        "options._id" : 0,
                        "stitchClass._id" : 0
                    }
                }
            ]

        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["stitch_point"].aggregate(query)]
        
        print(data)

        if data == []:
            response = jsonify({"message" : "Invalid argument!"})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(StitchInfo, "/v0/stvgodigital/pps3/techpack/info/sewing/stitch")

class LabelTypeMetadata(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("labelType", required = True, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        result = database["techpack"]["label_type"].aggregate(
            [
                {
                    "$match" : {
                        "code" : args["labelType"]
                    }
                },

                {
                    "$lookup" : {
                        "from" : "metadata",
                        "localField" : "metadata",
                        "foreignField" : "type",
                        "as" : "metadataType"
                    }
                },

                {
                    "$unwind" : "$metadataType"
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "metadataType.metadata" : 1
                    }
                }
            ]
        )

        data = None

        for r in result:
            data = r["metadataType"]["metadata"]

        if data is None:
            response = jsonify({"message" : "The provided labelType is not valid!"})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(LabelTypeMetadata, "/v0/stvgodigital/pps3/techpack/info/label/type/metadata")


class NeedleType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["needle"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(NeedleType, "/v0/stvgodigital/pps3/techpack/info/needle")


class SewingSpecificationInfo(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("garmentType", required = True, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = []

        result = database["techpack"]["sew_spec"].aggregate(
            [
                {
                    "$match" : {
                        "garmentType" : args["garmentType"]
                    }
                },

                {
                    "$lookup" : {
                        "from" : "specification_type",
                        "localField" : "code",
                        "foreignField" : "specReference",
                        "as" : "specificationType"
                    }
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "code" : 1,
                        "description" : 1,
                        "specificationType.type" : 1,
                        "specificationType.description" : 1,
                        "specificationType.img" : 1
                    }
                }
            ]
        )

        for r in result:
            data.append(r)
        
        if data == []:
            response = jsonify({"message" : "Invalid garmentType."})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(SewingSpecificationInfo, "/v0/stvgodigital/pps3/techpack/info/sewing/specification")


class OperationInfo(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("specType", required = False, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        if args["specType"] is None:
            query = [
                {
                    "$unwind" : "$specType"
                },

                {
                    "$group" : {
                        "_id" : "$specType",
                        "operations" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "specType" : "$_id",
                        "operations.code" : 1,
                        "operations.description" : 1
                    }
                }
            ]
        
        else:
            query = [
                {
                    "$unwind" : "$specType"
                },

                {
                    "$match" : {
                        "specType" : args["specType"]
                    }
                },

                {
                    "$group" : {
                        "_id" : "$specType",
                        "operations" : {
                            "$push" : "$$ROOT"
                        }
                    }
                },

                {
                    "$project" : {
                        "_id" : 0,
                        "specType" : "$_id",
                        "operations.code" : 1,
                        "operations.description" : 1
                    }
                }
            ]

        
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        result = database["techpack"]["operation_info"].aggregate(query)

        data = []

        for d in result:
            data.append(d)

        if data == []:
            response = jsonify({"message" : "Invalid specType."})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(OperationInfo, "/v0/stvgodigital/pps3/techpack/info/sewing/operation")


class OperationInfoMetadata(Resource):
    parser_get = reqparse.RequestParser()
    parser_get.add_argument("operationCode", required = False, location = "json")
    parser_get.add_argument("specType", required = False, location = "json")

    def get(self):
        args = self.parser_get.parse_args()

        data = None

        if args["operationCode"] is None and args["specType"] is None:
            response = jsonify({"message" : "You need to specify at least one of the arguments."})
            response.status_code = 406

            return response
        
        elif args["operationCode"] is not None:
            database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

            result = database["techpack"]["operation_info"].aggregate(
                [
                    {
                        "$unwind" : "$specType"
                    },

                    {
                        "$match" : {
                            "code" : args["operationCode"]
                        }
                    },

                    {
                        "$lookup" : {
                            "from" : "metadata",
                            "localField" : "metadata",
                            "foreignField" : "type",
                            "as" : "metadataType"
                        }
                    },

                    {
                        "$unwind" : "$metadataType"
                    },

                    {
                        "$project" : {
                            "_id" : 0,
                            "specType" : 1,
                            "code" : 1,
                            "metadata" : "$metadataType.metadata"
                        }
                    },

                    {
                        "$group" : {
                            "_id" : "$specType",
                            "operations" : {
                                "$push" : "$$ROOT"
                            }
                        }
                    },

                    {
                        "$project" : {
                            "operations.specType" : 0
                        }
                    },

                    {
                        "$project" : {
                            "_id" : 0,
                            "specType" : "$_id",
                            "operations" : 1
                        }
                    },
                ]
            )

            for r in result:
                data = r
        
        elif args["specType"] is not None:
            database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

            result = database["techpack"]["operation_info"].aggregate(
                [
                    {
                        "$unwind" : "$specType"
                    },

                    {
                        "$match" : {
                            "specType" : args["specType"]
                        }
                    },

                    {
                        "$lookup" : {
                            "from" : "metadata",
                            "localField" : "metadata",
                            "foreignField" : "type",
                            "as" : "metadataType"
                        }
                    },

                    {
                        "$unwind" : "$metadataType"
                    },

                    {
                        "$project" : {
                            "_id" : 0,
                            "specType" : 1,
                            "code" : 1,
                            "metadata" : "$metadataType.metadata"
                        }
                    },

                    {
                        "$group" : {
                            "_id" : "$specType",
                            "operations" : {
                                "$push" : "$$ROOT"
                            }
                        }
                    },

                    {
                        "$project" : {
                            "operations.specType" : 0
                        }
                    },

                    {
                        "$project" : {
                            "_id" : 0,
                            "specType" : "$_id",
                            "operations" : 1
                        }
                    },
                ]
            )

            for r in result:    
                data = r

        if data is None:
            response = jsonify({"message" : "The specified value is not valid!"})
            response.status_code = 406
        else:
            response = jsonify(data)
            response.status_code = 200

        return response

api.add_resource(OperationInfoMetadata, "/v0/stvgodigital/pps3/techpack/info/operation/metadata")


class PlacketView(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["placket_view"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(PlacketView, "/v0/stvgodigital/pps3/techpack/info/placket")


class PleatType(Resource):
    def get(self):
        database = pymongo.MongoClient(port = 27017, username = "root", password = "password")

        data = [d for d in database["techpack"]["pleat_type"].find({}, {"_id" : 0})]

        response = jsonify(data)
        response.status_code = 200

        return response

api.add_resource(PleatType, "/v0/stvgodigital/pps3/techpack/info/pleat")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=1234)