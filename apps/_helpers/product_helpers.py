def get_category_ancestors(category):
    ancestors = []
    current = category

    while current:
        ancestors.append(current)
        current = current.parent

    return ancestors[::-1] 



def get_descendants(category):
    descendants = []

    def collect(node):
        children = node.children.filter(is_active=True)
        for child in children:
            descendants.append(child)
            collect(child)

    collect(category)
    return descendants