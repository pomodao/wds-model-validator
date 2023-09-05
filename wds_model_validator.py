import bpy
import re
import textwrap 

bl_info = {
    "name": "Wonder Studio model validator",
    "author": "Pomo Rosso",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Help",
    "description": "Validate the file as a Wonder Studio character model",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Development"
}

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


def find_obj(root, name, obj_type=None):
    for obj in root:
        if obj_type is None or obj_type == obj.type:
            if (type(name) == re.Pattern and name.search(obj.name)) or name == obj.name:
                return obj
    return None


def show_message_box(messages=(), title='Message Box', icon='INFO'):
    def label_multiline(context, text, parent, indent=''):
        chars = int(context.region.width / 7)   # 7 pix on 1 character
        wrapper = textwrap.TextWrapper(width=chars, initial_indent=indent, subsequent_indent=indent)
        text_lines = wrapper.wrap(text=text)
        for text_line in text_lines:
            parent.label(text=text_line)

    def draw(self, context):
        for mes in messages:
            layout = self.layout
            label_multiline(context, mes[0], layout)
            print(mes[0])
            for p in mes[1:]:
                label_multiline(context, p, layout, '    ')
                print('\t' + p)

            layout.separator()

    if type(messages) is str:
        messages = ( messages, )
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def validate():
    messages = []

    character = find_obj(bpy.data.collections, ROOT_COLLECTION_NAME)
    if character is None:
        messages.append([f'[Error] Collection name: The character needs to be located in the collection named "{ROOT_COLLECTION_NAME}".'])
        return messages
    if len(character.children_recursive) != len(bpy.data.collections) - 1:
        messages.append(['[WARNING] Multiple root collections: There should be only one top collection name "character" you can put more collections inside it.'])

    body = find_obj(character.objects, re.compile('(.+_)?BODY'), 'ARMATURE')
    if body is None:
        messages.append(['[ERROR] Armature name: The character’s main armature needs to have a BODY tag in its name, for example, myCharacterName_BODY.'])
        return messages

    character_name = body.name.replace('_BODY', '')
    print(f'Character name: {character_name}')

    messages.extend(validate_bones(body.pose.bones))
    messages.extend(validate_object_name())
    messages.extend(validate_material_name())
    messages.extend(validate_image_name())

    return messages


def validate_bones(bones):
    def check_bones(ref, bones, parent_name):
        missing = []
        wrong = []
        rot_mode_error = []
        nonlocal hips_bone
        for key in ref.keys():
            # print(key, parent_name)
            if key not in bones:
                missing.append(key)
                continue
            target = bones[key]
            if parent_name is not None:
                if (target.parent.name != parent_name):
                    wrong.append(f'${key}(-> ${parent_name})')
            if target.rotation_mode != 'XYZ':
                rot_mode_error.append(key)
            if key == 'Hips':
                hips_bone = target.bone
            child = ref[key]
            m, w, r = check_bones(child, bones, key)
            missing.extend(m)
            wrong.extend(w)
            rot_mode_error.extend(r)

        return missing, wrong, rot_mode_error

    messages = []
    hips_bone = None

    missing, wrong, rot_mode_error = check_bones(VALID_BONES_STRUCTURE, bones, None)
    if len(missing) > 0:
        messages.append(['[WARNING] Bones not exist', ', '.join(missing)])
    if len(wrong) > 0:
        messages.append(['[WARNING] Wrong bone structure', ', '.join(wrong)])
    if len(rot_mode_error) > 0:
        messages.append(['[WARNING] Rotation mode error: Rotation mode for all main pose armature bones must be XYZ instead of WXYZ (QUATERNION), you can change this in pose mode', ', '.join(rot_mode_error)])
    if hips_bone is None or hips_bone.use_connect or not hips_bone.use_local_location:
        messages.append(['[WARNING] The Hips bone error: The Hips bone must be disconnected from its parent bone and local location turned on to allow for the translation of the character. Under Relations settings for the Hips bone, disable Connected option and enable Local Location option.'])
    
    return messages


def validate_object_name():
    errors = []

    dup_name_pattern = re.compile('\.\d+$')
    for o in bpy.data.objects:
        if dup_name_pattern.search(o.name):
            errors.append(o.name)

    if len(errors) > 0:
        return [['[ERROR] Objects can not have Blenders default duplicate name numeration in their name', ', '.join(errors)]]
    else:
        return []


def validate_material_name():
    errors = []

    mat_name_pattern = re.compile('_MAT$')
    for m in bpy.data.materials:
        if not mat_name_pattern.search(m.name) and not m.is_grease_pencil:
            errors.append(m.name)

    if len(errors) > 0:
        return [['[ERROR] Materials need to have a `MAT` tag in their name', ', '.join(errors)]]
    else:
        return []


def validate_image_name():
    errors = []

    image_name_pattern = re.compile('_TEX_(AO|ANITROPROT|ANITROP|BUMP|COATWEIGHT|DIFF|DISPLACE|EMISSION|EMISSIONWEIGHT|IOR|METAL|NORM|OPAC|ROUGH|SPEC|SSS|THICK|TRANSWEIGHT)\.\w+$')
    for i in bpy.data.images:
        if not image_name_pattern.search(i.name) and i.filepath != '':
            errors.append(i.name)

    if len(errors) > 0:
        return [['[ERROR] Image textures need to use the following template: [matName][_description][_udim]_TEX_[type].[ext]', ', '.join(errors)]]
    else:
        return []


class WDSValidator_OT_Validate(bpy.types.Operator):

    bl_idname = "outliner.wdsvalidator_validate"
    bl_label = "Wonder Studio model validator"
    bl_description = "Validate the file as a Wonder Studio character model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        messages = validate()
        if len(messages) == 0:
            messages = [['[OK] No errors found.']]
        show_message_box(title='WD Model Validator', icon='INFO', messages=messages)

        return {'FINISHED'}


def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(WDSValidator_OT_Validate.bl_idname)


classes = [
    WDSValidator_OT_Validate,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    # bpy.types.OUTLINER_MT_collection.append(menu_fn)
    bpy.types.TOPBAR_MT_help.append(menu_fn)


def unregister():
    # bpy.types.OUTLINER_MT_collection.remove(menu_fn)
    bpy.types.TOPBAR_MT_help.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
