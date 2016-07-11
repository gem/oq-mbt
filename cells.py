from serial import Dictable
from IPython.display import display, Javascript
import json

def cells_cleanall():
    display(Javascript("""
      {
          var cells = IPython.notebook.get_cells();
          var ctx, ct = cells.length;
          for (var i = 0 ; i < ct ; i++) {
              if (i == 0) {
                  cells[i].unselect();
              }
              else {
                  cells[i].select();
              }
          }
          IPython.notebook.delete_cell();
      }
    """))


def cells_insert_at_bottom(type, content):
    display(Javascript("""
    {
    var cell = IPython.notebook.insert_cell_at_bottom('%s');
    cell.set_text(%s);
    }
    """ % (type, json.dumps(content))))

            
class Cell(Dictable):
    __public__ = ["type", "content"]

    def __init__(self, type, content):
        self.type = type
        self.content = content

        
class Cells(Dictable):
    __public__ = ["cells"]

    def __init__(self, cells=None):
        if cells is None:
            self.cells = []
        else:
            self.cells = cells


    def load(self):
        cells_cleanall()
        for cell in self.cells:
            cells_insert_at_bottom(cell.type, cell.content)
