"""API Doc templates generator."""


class HydraDoc():
    """Template for a new API Doc."""

    def __init__(self, API, title, desc, entrypoint, base_url):
        """Initialize the Hydra_APIDoc."""
        self.API = API
        self.title = title
        self.base_url = base_url
        self.context = Context(base_url + API)
        self.parsed_classes = list()
        self.other_classes = list()
        self.collections = list()
        self.status = list()
        self.entrypoint = HydraEntryPoint(entrypoint)
        self.desc = desc

    def add_supported_class(self, class_, collection=False):
        """Add a new supportedClass."""
        # self.doc["supportedClass"].append(class_.get())
        self.parsed_classes.append(class_)
        if collection:
            collection = HydraCollection(class_)
            self.collections.append(collection)

    def add_possible_status(self, status):
        """Add a new possibleStatus."""
        self.status.append(status)

    def add_baseCollection(self):
        """Add Collection class to the API Doc."""
        collection = HydraClass("http://www.w3.org/ns/hydra/core#Collection", "Collection", None)
        member = HydraClassProp("http://www.w3.org/ns/hydra/core#member", "members", False, False, None)
        collection.add_supported_prop(member)
        self.other_classes.append(collection)

    def add_baseResource(self):
        """Add Resource class to the API Doc."""
        resource = HydraClass("http://www.w3.org/ns/hydra/core#Resource", "Resource", None)
        self.other_classes.append(resource)

    def add_to_context(self, key, value):
        """Add entries to the vocabs context."""
        self.context.add(key, value)

    def gen_EntryPoint(self):
        """Generate the EntryPoint for the Hydra Doc."""
        for class_ in self.parsed_classes:
            if class_.endpoint:
                self.entrypoint.add_Class(class_)
        for collection in self.collections:
            self.entrypoint.add_Collection(collection)
        # pdb.set_trace()

    def generate(self):
        """Get the Hydra API Doc as a python dict."""
        doc = {
            "@context": self.context.generate(),
            "@id": self.base_url + self.API + "/vocab",
            "@type": "ApiDocumentation",
            "title": self.title,
            "description": self.desc,
            "entrypoint": self.entrypoint.url,
            "supportedClass": [x.generate() for x in self.parsed_classes + self.other_classes + self.collections + [self.entrypoint]],
            "possibleStatus": [x.generate() for x in self.status]
        }
        return doc


class HydraClass():
    """Template for a new class."""

    def __init__(self, id_, title, desc,  endpoint=False, sub_classof=None):
        """Initialize the Hydra_Class."""
        self.id_ = id_
        self.title = title
        self.desc = desc
        self.parents = None
        self.endpoint = endpoint
        self.supportedProperty = list()
        self.supportedOperation = list()
        if sub_classof is not None:
            self.parents = sub_classof

    def add_supported_prop(self, prop):
        """Add a new supportedProperty."""
        self.supportedProperty.append(prop)

    def add_supported_op(self, op):
        """Add a new supportedOperation."""
        self.supportedOperation.append(op)

    def generate(self):
        """Get the Hydra class as a python dict."""
        class_ = {
            "@id": self.id_,
            "@type": "hydra:Class",
            "subClassOf": self.parents,
            "title": self.title,
            "description": self.desc,
            "supportedProperty": [x.generate() for x in self.supportedProperty],
            "supportedOperation": [x.generate() for x in self.supportedOperation],
        }
        return class_


class HydraClassProp():
    """Template for a new property."""

    def __init__(self, prop, title, read, write, required):
        """Initialize the Hydra_Prop."""
        self.prop = prop
        self.title = title
        self.read = read
        self.write = write
        self.required = required

    def generate(self):
        """Get the Hydra prop as a python dict."""
        prop = {
          "@type": "SupportedProperty",
          "title": self.title,
          "property": self.prop,
          "required": self.required,
          "readable": self.read,
          "writeable": self.write
        }
        return prop


class HydraClassOp():
    """Template for a new supportedOperation."""

    def __init__(self, title, method, expects, returns, status):
        """Initialize the Hydra_Prop."""
        self.title = title
        self.method = method
        self.expects = expects
        self.returns = returns
        self.status = status

    def generate(self):
        """Get the Hydra op as a python dict."""
        op = {
                "@type": "hydra:Operation",
                "title": self.title,
                "method": self.method,
                "expects": self.expects,
                "returns": self.returns,
                "possibleStatus": self.status
        }
        return op


class HydraCollection():
    """Class for Hydra Collection."""

    def __init__(self, class_):
        """Generate Collection for a given class."""
        self.class_ = class_
        self.name = class_.title

    def generate(self):
        """Get as a python dict."""
        collection = {
            "@id": "vocab:%sCollection" % (self.name,),
            "@type": "hydra:Class",
            "subClassOf": "http://www.w3.org/ns/hydra/core#Collection",
            "label": "%sCollection" % (self.name),
            "description": "A collection of %s" % (self.name.lower()),
            "supportedOperation": [
                {
                    "@id": "_:%s_create" % (self.name.lower()),
                    "@type": "http://schema.org/AddAction",
                    "method": "POST",
                    "description": None,
                    "expects": self.name,
                    "returns": self.name,
                    "statusCodes": [
                        {
                            "code": 201,
                            "description": "If the %s entity was created successfully." % (self.name,)
                        }
                    ]
                },
                {
                    "@id": "_:%s_collection_retrieve" % (self.name.lower(),),
                    "@type": "hydra:Operation",
                    "method": "GET",
                    "label": "Retrieves all %s entities" % (self.name,),
                    "description": None,
                    "expects": None,
                    "returns": "vocab:%sCollection" % (self.name),
                    "statusCodes": [
                    ]
                }
            ],
            "supportedProperty": [
                {
                    "property": "http://www.w3.org/ns/hydra/core#member",
                    "hydra:title": "members",
                    "hydra:description": "The %s" % (self.name.lower(),),
                    "required": None,
                    "readonly": False,
                    "writeonly": False

                }
            ]
        }
        return collection


class HydraEntryPoint():
    """Template for a new entrypoint."""

    def __init__(self, url):
        """Initialize the Entrypoint."""
        self.url = url
        self.entrypoint = HydraClass("vocab:EntryPoint", "EntryPoint", "The main entry point or homepage of the API.")
        self.entrypoint.add_supported_op(EntryPointOp("_:entry_point", "GET", "The APIs main entry point.", None, None, "vocab:EntryPoint"))

    def get(self):
        """Get the Hydra prop as a python dict."""
        return self.prop

    def add_Class(self, class_):
        """Add supportedProperty to the EntryPoint."""
        entrypoint_class = EntryPointClass(class_)
        self.entrypoint.add_supported_prop(entrypoint_class)

    def add_Collection(self, collection):
        """Add supportedProperty to the EntryPoint."""
        entrypoint_collection = EntryPointCollection(collection)
        self.entrypoint.add_supported_prop(entrypoint_collection)

    def generate(self):
        """Get as a Python dict."""
        return self.entrypoint.generate()


class Context():
    """Class for JSON-LD context."""

    def __init__(self, address, adders={}):
        """Initialize context."""
        # NOTE: adders is a dictionary containing additional context elements to the base Hydra context
        self.context = {
            "hydra": "http://www.w3.org/ns/hydra/core#",
            "property": {
                "@type": "@id",
                "@id": "hydra:property"
            },
            "supportedClass": "hydra:supportedClass",
            "supportedProperty": "hydra:supportedProperty",
            "supportedOperation": "hydra:supportedOperation",
            "code": "hydra:statusCode",
            "label": "rdfs:label",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "vocab": address + "/vocab#",
            # "vocab": "localhost/api/vocab#",
            "domain": {
                "@type": "@id",
                "@id": "rdfs:domain"
            },
            "ApiDocumentation": "hydra:ApiDocumentation",
            "range": {
                "@type": "@id",
                "@id": "rdfs:range"
            },
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "title": "hydra:title",
            "readonly": "hydra:readonly",
            "expects": {
                "@type": "@id",
                "@id": "hydra:expects"
            }
        }

    def generate(self):
        """Get as a python dict."""
        return self.context

    def add(self, key, value):
        """Add entry to context."""
        self.context[key] = value


class EntryPointCollection():
    """Class for a Collection Entry to the EntryPoint object."""

    def __init__(self, collection):
        """Create method."""
        self.collection = collection
        self.name = collection.name

    def generate(self):
        """Get as a python dict."""
        object_ = {
            "property": {
                "@id": "vocab:EntryPoint/" + self.name,
                "@type": "hydra:Link",
                "label": self.name,
                "description": "The %s collection" % (self.name,),
                "domain": "vocab:EntryPoint",
                "range": "vocab:%sCollection" % (self.name,),
                "supportedOperation": [
                    {
                        "@id": "_:%s_collection_retrieve" % (self.name.lower(),),
                        "@type": "hydra:Operation",
                        "method": "GET",
                        "label": "Retrieves all %s entities" % (self.name,),
                        "description": None,
                        "expects": None,
                        "returns": "vocab:%sCollection" % (self.name,),
                        "statusCodes": [
                        ]
                    }
                ]
            },
            "hydra:title": self.name.lower(),
            "hydra:description": "The %s collection" % (self.name,),
            "required": None,
            "readonly": True,
            "writeonly": False
        }
        return object_


class EntryPointClass():
    """Class for a Operation Entry to the EntryPoint object."""

    def __init__(self, class_):
        """Create method."""
        self.name = class_.title
        self.desc = class_.desc
        self.supportedOperation = class_.supportedOperation

    def generate(self):
        """Get as Python Dict."""
        object_ = {
            "property": {
                "@id": "vocab:EntryPoint/" + self.name,
                "@type": "hydra:Link",
                "label": self.name,
                "description": self.desc,
                "domain": "vocab:EntryPoint",
                "range": "vocab:%sCollection" % (self.name),
                "supportedOperation": []
            },
            "hydra:title": self.name.lower(),
            "hydra:description": "The %s Class" % (self.name),
            "required": None,
            "readonly": True,
            "writeonly": False
        }
        for op in self.supportedOperation:
            operation = EntryPointOp("_:"+op.title.lower(), op.method, op.title, None, op.expects, op.returns, op.status)
            object_["property"]["supportedOperation"].append(operation.generate())
        return object_


class EntryPointOp():
    """supportedOperation for EntryPoint."""

    def __init__(self, id_, method, label, desc, expects, returns, statusCodes=[]):
        """Create method."""
        self.id_ = id_
        self.method = method
        self.label = label
        self.desc = desc
        self.expects = expects
        self.returns = returns
        self.statusCodes = statusCodes

    def generate(self):
        """Get as Python Dict."""
        prop = {
            "@id": self.id_,
            "@type": "hydra:Operation",
            "method": self.method,
            "label": self.label,
            "description": self.desc,
            "expects": self.expects,
            "returns": self.returns,
            "statusCodes": self.statusCodes
        }
        return prop


class HydraStatus():
    """Class for possibleStatus in Hydra Doc."""

    def __init__(self, code, title, desc):
        """Create method."""
        self.code = code
        self.title = title
        self.desc = desc

    def generate(self):
        """Get as Python dict."""
        status = {
          "@context": "http://www.w3.org/ns/hydra/context.jsonld",
          "@type": "Status",
          "statusCode": self.code,
          "title": self.title,
          "description": self.desc,
        }
        return status
