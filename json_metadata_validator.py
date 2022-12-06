import re

class JsonMetadataValidator:
    def __init__(self, metadata) -> None:
        self.metadata = metadata

    def _validateValues(self, valueObj, valueMetadata):
        if valueMetadata["type"] == "string":
            if type(valueObj) != str:
                return False

            if "pattern" in valueMetadata and re.search(valueMetadata["pattern"], valueObj) is None:
                return False
            
        elif valueMetadata["type"] == "float" and type(valueObj) != float:
            return False
        
        elif valueMetadata["type"] == "integer" and type(valueObj) != int:
            return False
        
        elif valueMetadata["type"] == "object":
            if type(valueObj) != dict:
                return False
            else:
                check = self.validateJsonMetadata(valueObj, valueMetadata["properties"])

                if not check:
                    return False
    
        elif valueMetadata["type"] == "list":
            if type(valueObj) != list:
                return False
            else:
                try:
                    check = self._validateValues(valueObj[0], valueMetadata["element"])
                except IndexError:
                    if valueMetadata["element"]["required"]:
                        return False
                    
                    check = True
                
                if not check:
                    return False
        
        return True

    def validateJsonMetadata(self, jsonObj, metadata = None):
        if metadata is None:
            metadata = self.metadata

        for key, info in metadata.items():
            
            if key not in jsonObj.keys() and info["required"] == True:
                return False

            if key in jsonObj.keys():
                check = self._validateValues(jsonObj[key], info)

                if not check:
                    return False

            del jsonObj[key]

        if jsonObj != {}:
            return False
            
        return True           