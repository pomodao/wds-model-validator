import bpy
import re
import warnings

ROOT_COLLECTION_NAME = 'character'
VALID_BONES_STRUCTURE = {
    'Hips': {
        'Spine': {
            'Spine1': {
                'Spine2': {
                    'Neck': {
                        'Head': {}
                    },
                    'LeftShoulder': {
                        'LeftArm': {
                            'LeftForeArm': {
                                'LeftHand_IK': {},
                                'LeftHand': {
                                    'LeftHandThumb1': {
                                        'LeftHandThumb2': {
                                            'LeftHandThumb3': {}
                                        }
                                    },
                                    'LeftHandIndex1': {
                                        'LeftHandIndex2': {
                                            'LeftHandIndex3': {}
                                        }
                                    },
                                    'LeftHandMiddle1': {
                                        'LeftHandMiddle2': {
                                            'LeftHandMiddle3': {}
                                        }
                                    },
                                    'LeftHandRing1': {
                                        'LeftHandRing2': {
                                            'LeftHandRing3': {}
                                        }
                                    },
                                    'LeftHandPinky1': {
                                        'LeftHandPinky2': {
                                            'LeftHandPinky3': {}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'RightShoulder': {
                        'RightArm': {
                            'RightForeArm': {
                                'RightHand_IK': {},
                                'RightHand': {
                                    'RightHandThumb1': {
                                        'RightHandThumb2': {
                                            'RightHandThumb3': {}
                                        }
                                    },
                                    'RightHandIndex1': {
                                        'RightHandIndex2': {
                                            'RightHandIndex3': {}
                                        }
                                    },
                                    'RightHandMiddle1': {
                                        'RightHandMiddle2': {
                                            'RightHandMiddle3': {}
                                        }
                                    },
                                    'RightHandRing1': {
                                        'RightHandRing2': {
                                            'RightHandRing3': {}
                                        }
                                    },
                                    'RightHandPinky1': {
                                        'RightHandPinky2': {
                                            'RightHandPinky3': {}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        'LeftUpLeg': {
            'LeftLeg': {
                'LeftFoot_IK': {},
                'LeftFoot': {
                    'LeftToeBase': {}
                }
            }
        },
        'RightUpLeg': {
            'RightLeg': {
                'RightFoot_IK': {},
                'RightFoot': {
                    'RightToeBase': {}
                }
            }
        }
    }
}


def print_info(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'INFO':
                print('data', data)

def find_obj(root, name, obj_type=None):
    for obj in root:
        if obj_type is None or obj_type == obj.type:
            if (type(name) == re.Pattern and name.match(obj.name)) or name == obj.name:
                return obj
    return None

def ShowMessageBox(messages = (), title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        for m in messages:
            self.layout.label(text=m)

    if type(messages) is str:
        messages = ( messages, )
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


##Shows a message box with a specific message 
#ShowMessageBox("This is a message") 

##Shows a message box with a message and custom title
#ShowMessageBox("This is a message", "This is a custom title")

#Shows a message box with a message, custom title, and a specific icon
#ShowMessageBox(
#    "This is a message.\r\n\nThis is also a message.",
#    "This is a custom title",
#    'ERROR')


# Naming Requirements
character = find_obj(bpy.data.collections, ROOT_COLLECTION_NAME)
assert character is not None, f'The character needs to be located in the collection named "{ROOT_COLLECTION_NAME}".'


body = find_obj(character.objects, re.compile('(.+_)?BODY'), 'ARMATURE')
assert body is not None, 'The character’s main armature needs to have a BODY tag in its name, for example, myCharacterName_BODY.'
print(body)
character_name = body.name.replace('_BODY', '')
print(character_name)

bones = body.pose.bones

assert bones['Hips'] is not None, 'Hips'
print_info("hello")

def validate_bones(ref, bones, parent_name):
    for key in ref.keys():
        print(key, parent_name)
        assert key in bones, f'"${key}" is not exist'
        target = bones[key]
        if parent_name is not None:
            assert target.parent.name == parent_name, f"{key}'s parent must be {parent_name}"
        child = ref[key]
        validate_bones(child, bones, key)

validate_bones(VALID_BONES_STRUCTURE, bones, None)

ShowMessageBox(title='WD Model Validator', icon='INFO', messages='hello')

ShowMessageBox(title='WD Model Validator', icon='INFO', messages=('hello', 'world'))
