from propertyChangeEvent import *


def readProperties(db, queue):
    """ Fetch the most recent values of all properties and replay them to update dynamic state of reconfigurable components """
    
    sql = """
    select lh.propertyName, rh.propertyValue from 
      (
         select propertyName 
         from properties 
         group by propertyName
      ) lh
    left join properties rh on lh.propertyName = rh.propertyName 
    where rh.lastUpdated=
      (
         select max(ss.lastUpdated) 
         from properties ss 
         where ss.propertyName = lh.propertyName
      ) ;
    """
    c = db.cursor();
    c.execute(sql);
    for property in c.fetchall():
        event = PropertyChangeEvent(property[0], property[1], True)
        queue.processEvent(event)