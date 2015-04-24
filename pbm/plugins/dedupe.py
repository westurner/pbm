
import collections
import logging

import pbm.plugins

log = logging.getLogger(__name__)


class DedupeObj(object):

    def __init__(self):
        self.dict = collections.OrderedDict()

    def is_duplicate_bookmark(self, node):
        if node.get('type') == 'url':
            url = node.get('url')
            date = node.get('date_added')
            key = (url, date)
            if key not in self.dict:
                self.dict[key] = True
                return False
            else:
                log.debug("duplicate: %r" % node)
                return True
        else:
            raise Exception(node)
            return False


class DedupePlugin(pbm.plugins.PromiumPlugin):

    def preprocess_bookmarks(self, bookmarks_obj):
        bookmarks_dict = bookmarks_obj.bookmarks_dict
        bookmarks_obj.bookmarks_dict = (
            self.dedupe_bookmarks_dict(bookmarks_dict))
        return bookmarks_obj

    @staticmethod
    def dedupe_bookmarks_list(bookmarks_list):
        dedupe_dict = collections.OrderedDict()
        for bookmark in bookmarks_list:
            url = bookmark.get('url')
            date = bookmark.get('date')
            key = (url, date)
            if key not in dedupe_dict:
                dedupe_dict[key] = bookmark
            else:
                continue
        return pbm.utils.itervalues(dedupe_dict)

    @staticmethod
    def dedupe_bookmarks_dict(bookmarks_dict):
        DedupePlugin.walk_and_dedupe_bookmarks(
            bookmarks_dict['roots']['bookmark_bar'])
        DedupePlugin.walk_and_dedupe_bookmarks(
            bookmarks_dict['roots']['other'])
        return bookmarks_dict

    @staticmethod
    def walk_and_dedupe_bookmarks(node, dedupe_obj=None, folder=None):
        """
        Walk a Chromium Bookmarks dict recursively; removing duplicates
        (where type=='url' and (url, date) are the same)

        Args:
            node (dict): dict to traverse (type:url|folder, children:[]])

        Keyword Arguments:
            dedupe_obj (DedupeObj): obj w/ is_duplicate_bookmark method
            folder (dict): current folder dict

        .. note:: This function has side effects (it mutates the nodes)

        """
        if dedupe_obj is None:
            dedupe_obj = DedupeObj()
        _type = node.get('type')
        if _type == 'folder':
            folder = node
            for item in node['children'] or []:
                if not (item and hasattr(item, 'get') and 'type' in item):
                    continue
                _item_type = item.get('type')
                if _item_type == 'folder':
                    DedupePlugin.walk_and_dedupe_bookmarks(
                        item,
                        dedupe_obj=dedupe_obj,
                        folder=folder)
                elif _item_type == 'url':
                    if dedupe_obj.is_duplicate_bookmark(item):
                        _len_before = len(folder['children'])
                        folder['children'].remove(item)
                        _len_after = len(folder['children'])
                        if _len_after >= _len_before:
                            raise Exception(folder['children'])
        elif _type == 'url':
            if dedupe_obj.is_duplicate_bookmark(node):
                if folder is None:
                    raise Exception('folder is None')
                folder['children'].remove(node)
