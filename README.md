# VYUHIIKA APPS


#########################################
                Endpoints
#########################################

* Server Health Status Check.
    - ENDPOINT: /health 
    - METHOD: GET
    - REQUEST: Null
    - RESPONSE: {
            "status": str,
            "errors": {
                "msg": str
            }
        }

* JSON Validator
    - ENDPOINT: /api/v1/json-validator/validate
    - METHOD: POST
    - REQUEST: {
        schema: object,
        data: object
    }
    - RESPONSE: {
        "valid": bool,
        "errors": [
            {
                "path": str,
                "message: str
            }
        ]
    }