import sqlalchemy

COLS_IGNORE_LIST = ["_sa_instance_state"]

class DataTable():
    
    def __init__(self, data, db, dbClass, searchHelperClass, truncateUid=False):

        self.db                = db
        self.draw              = int(data["draw"])
        self.start             = int(data["start"])
        self.length            = int(data["length"])
        self.trueLength        = -1
        self.dbClass           = dbClass
        self.searchHelperClass = searchHelperClass
        self.orderByCol        = int(data["order[0][column]"])
        self.searchValue       = data["search[value]"]
        self.searchIsRegex     = data["search[regex]"]
        self.orderDirection    = data["order[0][dir]"]

        self.truncateUid = truncateUid

        self.cols = DataTable.staticGetCols(dbClass)

        # order variable for use with python sorted etc #
        self.orderAsc = self.orderDirection == "asc"

        # oder variable for use with sqlalchemy
        if self.orderAsc:
            self.orderAscDbClass = sqlalchemy.asc
        else:
            self.orderAscDbClass = sqlalchemy.desc

    def staticGetCols(dbClass):
        cols = list(dbClass.__table__.columns.keys())
        return list(filter(lambda c: c not in COLS_IGNORE_LIST, cols))

    def __build(self, results, total, filtered):

        self.cacheResults = results
        
        count = 0
        resultDicts = [ r.__dict__ for r in results ]

        # data list must have the correct order (same as table scheme) #
        rows = []
        for r in resultDicts:
            singleRow = []
            for key in self.cols:
                if key == "uid" and self.truncateUid:
                    singleRow.append(r[key][:8])
                else:
                    singleRow.append(r[key])
            rows.append(singleRow)

        d = dict()
        d.update({ "draw" : self.draw })
        d.update({ "recordsTotal" : total })
        d.update({ "recordsFiltered" :  filtered })
        d.update({ "data" : rows })

        return d

    def get(self):

        filtered = 0
        total    = 0

        if self.searchValue:

            # base query
            query = self.db.session.query(self.searchHelperClass.uid)
            total = query.count()

            # search string (search for all substrings individually #
            filterQuery = query
            for substr in self.searchValue.split(" "):
                searchSubstr = "%{}%".format(substr.strip())
                filterQuery  = filterQuery.filter(
                                    self.searchHelperClass.fullstring.like(searchSubstr))

            # uidList  = filterQuery.all()
            filtered = filterQuery.count()

            # get relevant pIds from searchHelper #
            uidList = filterQuery.offset(self.start).limit(self.length).all()

            # use pIds to retrive full information #
            results = []
            for uidTup in uidList:
                uid = uidTup[0]
                singleResult = self.db.session.query(self.dbClass).filter(
                                    self.dbClass.uid == uid).first()
                if singleResult:
                    results.append(singleResult)
                
                col = self.dbClass.__table__.c[self.orderByCol]
                results = sorted(results, 
                                    key=lambda row: self.getColByNumber(row, self.orderByCol), 
                                    reverse=not self.orderAsc)
        else:

            query = self.db.session.query(self.dbClass)
            if self.orderByCol:
                query  = query.order_by(self.orderAscDbClass(
                            list(self.dbClass.__table__.c)[self.orderByCol]))
            else:
                query  = query.order_by(self.orderAscDbClass(
                            list(self.dbClass.__table__.c)[0]))

            results  = query.offset(self.start).limit(self.length).all()
            total    = query.count()
            filtered = total

        return self.__build(results, total, filtered)

    def getColByNumber(self, dbClass, nr):
        nr = int(nr)
        value = getattr(dbClass, self.cols[nr])
        return value
