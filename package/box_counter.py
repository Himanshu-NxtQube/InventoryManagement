
class BoxCounter:
    def __init__(self):
        pass

    def estimate_box_count(self, inventory_df, batch_id, status, stack_count):
        if batch_id == None:
            return None
        
        box_per_stack = inventory_df[batch_id]['Max Boxes']/inventory_df[batch_id]['Max Layer']
        print(batch_id)
        print("Box per stack", box_per_stack)
        print("Stack count:", stack_count)
        if status == 'full':
            return stack_count * box_per_stack
        elif status == 'partial':
            return [(stack_count - 1) * box_per_stack, stack_count * box_per_stack]
