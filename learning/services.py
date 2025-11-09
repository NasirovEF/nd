def add_doc_url(instance, file_name):
    if not instance.branch or instance.branch is None:
        return f"learning/{instance.__class__.__name__}/{instance.organization.pk}/{file_name}"
    elif not instance.division or instance.division is None:
        return f"learning/{instance.__class__.__name__}//{instance.organization.pk}/{instance.branch.pk}/{file_name}"
    elif not instance.district or instance.district is None:
        return f"learning/{instance.__class__.__name__}//{instance.organization.pk}/{instance.branch.pk}/{instance.division.pk}/{file_name}"
    elif not instance.group or instance.group is None:
        return f"learning/{instance.__class__.__name__}//{instance.organization.pk}/{instance.branch.pk}/{instance.division.pk}/{instance.district.pk}/{file_name}"
    else:
        return f"learning/{instance.__class__.__name__}//{instance.organization.pk}/{instance.branch.pk}/{instance.division.pk}/{instance.district.pk}/{instance.group.pk}/{file_name}"
