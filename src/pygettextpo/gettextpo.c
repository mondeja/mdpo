/* Copyright Canonical Ltd.  This software is licensed under the GNU
   Affero General Public License version 3 (see the file LICENSE). */

/* -*- mode: C; c-basic-offset: 4 -*- */
#include <Python.h>
#include <pythread.h>

#include <stdarg.h>
#include <setjmp.h>

#include <gettext-po.h>

#define MIN_REQUIRED_GETTEXTPO_VERSION 0x000F00

#if LIBGETTEXTPO_VERSION < MIN_REQUIRED_GETTEXTPO_VERSION
#  error "this module requires gettext >= 0.15"
#endif

static PyObject *gettextpo_error = NULL;

typedef struct {
    PyObject_HEAD
    po_file_t pofile;
} PyPoFile;
static PyTypeObject PyPoFile_Type;

typedef struct {
    PyObject_HEAD
    po_message_iterator_t iter;
    PyObject *pofile;
} PyPoMessageIterator;
static PyTypeObject PyPoMessageIterator_Type;

typedef struct {
    PyObject_HEAD
    po_message_t msg;
    PyObject *pofile;
} PyPoMessage;
static PyTypeObject PyPoMessage_Type;

/* ---------------------------- */

/**
 * get_pybytes_from_pyobject:
 * @object: a PyObject that represents a PyUnicode object.
 *
 * Gets a PyBytes that represents the @object as UTF-8.  If the
 * object is a PyBytes, then assume it is in UTF-8 and return it.
 *
 * Return value: a new #PyBytes object or NULL if there is any error
 * in which case, PyErr is set.
 **/
static PyObject *
get_pybytes_from_pyobject(PyObject *object)
{
    PyObject *unicode;
    PyObject *string;

    if (PyBytes_Check(object)) {
	    Py_INCREF(object);
	    return object;
    }

    unicode = PyUnicode_FromObject(object);

    if (unicode == NULL)
        return NULL;

    string = PyUnicode_AsUTF8String(unicode);

    Py_DECREF(unicode);
    return string;
}

/* XXXX TODO: currently I've only implemented the "error" function for
 * the handler, but this is all that po_message_check_format() uses
 * currently. */

typedef struct {
    jmp_buf env;
    PyObject *error_list;
    PyObject *error_string;
} ErrorClosure;

/* Access to this variable is controlled by error_closure_lock.
 *
 * The underlying libgettextpo library is not thread safe with respect
 * to the handling of error callbacks.
 *
 * At the moment, we aren't doing anything that would cause the
 * interpreter to drop the GIL so it probably isn't needed in
 * practice, but this way we won't get weird problems if we start
 * running a Python code from an error handler in the future ...
 */
static ErrorClosure *error_closure = NULL;
static PyThread_type_lock error_closure_lock= NULL;

static void
error_handler_xerror(int severity, po_message_t message,
		     const char *filename, size_t lineno, size_t column,
		     int multiline_p, const char *message_text)
{
    PyObject *str;

    /* printf the string */
    {
        size_t size = strlen(message_text);
        if (size > PY_SSIZE_T_MAX)
            /* We can't raise an exception here, so just truncate it. */
            size = PY_SSIZE_T_MAX;
        str = PyUnicode_DecodeUTF8(message_text, (Py_ssize_t)size, "replace");
    }

    /* store the errors in a list, and as a string */
    PyList_Append(error_closure->error_list, Py_BuildValue("(siO)",
        severity == PO_SEVERITY_WARNING ? "warning" : "error", 0, str));

    {
	PyObject *old_error_string = error_closure->error_string;
	if (PyUnicode_GET_LENGTH(error_closure->error_string)) {
	    error_closure->error_string = PyUnicode_FromFormat(
		"%U\n%U", error_closure->error_string, str);
	    Py_XDECREF(str);
	} else
	    error_closure->error_string = str;
	    Py_XDECREF(old_error_string);
    }

    /* if it is a fatal error, we are not meant to return */
    if (severity == PO_SEVERITY_FATAL_ERROR) {
	    fprintf(stderr, "error_handler_error: severity == "
		    "PO_SEVERITY_FATAL_ERROR, longjmp'ing out\n");
	    longjmp(error_closure->env, 1);
    }
}

struct po_xerror_handler error_handler = {
    .xerror = error_handler_xerror,
};

/* ---------------------------- */

static int
pypo_file_init(PyPoFile *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "filename", NULL };
    int ret = 0;
    const char *filename = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|z:__init__", kwlist,
				     &filename)) {
	    return -1;
    }

    if (filename) {
        ErrorClosure closure;

        closure.error_list = PyList_New(0);
        closure.error_string = PyUnicode_FromString("");

        PyThread_acquire_lock(error_closure_lock, WAIT_LOCK);
        error_closure = &closure;

        if (setjmp(closure.env) == 0) {
            self->pofile = po_file_read(filename, &error_handler);
        }

        error_closure = NULL;
        PyThread_release_lock(error_closure_lock);

        if (PyUnicode_GetLength(closure.error_string) != 0) {
            PyObject *exc;

            /* set up the exception */
            exc = PyObject_CallFunction(gettextpo_error,
                        "O", closure.error_string);
            PyObject_SetAttrString(exc, "error_list", closure.error_list);
            PyErr_SetObject(gettextpo_error, exc);
            ret = -1;
        } else {
            Py_INCREF(Py_None);
            ret = 0;
        }
        Py_DECREF(closure.error_list);
        Py_DECREF(closure.error_string);
    } else {
	    self->pofile = po_file_create();
    }

    if (ret == 0 && self->pofile == NULL) {
        PyErr_SetString(PyExc_RuntimeError,
                "could not create PoFile object");
        ret = -1;
    }

    return ret;
}

static void
pypo_file_dealloc(PyPoFile *self)
{
    if (self->pofile != NULL) {
	    po_file_free(self->pofile);
        self->pofile = NULL;
    }

    PyObject_Del(self);
}

static PyObject *
py_po_file_iter(PyPoFile *self)
{
    PyPoMessageIterator *iter;

    iter = PyObject_New(PyPoMessageIterator, &PyPoMessageIterator_Type);
    if (!iter) return NULL;

    po_file_t a = self->pofile;

    printf("a = %p\n", a);
    //printf("a->iter = %p", a->iter);
    iter->iter = po_message_iterator(self->pofile, NULL);
    if (!iter->iter) {
	Py_DECREF(iter);
	PyErr_SetString(PyExc_RuntimeError,
			"could not create message iterator");
	return NULL;
    }
    Py_INCREF(self);
    iter->pofile = (PyObject *)self;
    return (PyObject *)iter;
}

PyDoc_STRVAR(doc_pypo_file_write,
"F.write(filename) -> None.  Write contents of PoFile to a file on\n"
"disk.\n"
"\n"
"Raises gettextpo.error on error.");

/* This function depends on the Python Global Interpreter Lock for
 * synchronising access to the "error_closure" global variable. */
static PyObject *
pypo_file_write(PyPoFile *self, PyObject *args)
{
    const char *filename;
    ErrorClosure closure;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s:write", &filename))
	return NULL;

    closure.error_list = PyList_New(0);
    closure.error_string = PyUnicode_FromString("");

    PyThread_acquire_lock(error_closure_lock, WAIT_LOCK);
    error_closure = &closure;

    if (setjmp(closure.env) == 0) {
	po_file_write(self->pofile, filename, &error_handler);
    }

    error_closure = NULL;
    PyThread_release_lock(error_closure_lock);

    if (PyUnicode_GetLength(closure.error_string) != 0) {
	PyObject *exc;

	/* set up the exception */
	exc = PyObject_CallFunction(gettextpo_error,
				    "O", closure.error_string);
	PyObject_SetAttrString(exc, "error_list", closure.error_list);

	PyErr_SetObject(gettextpo_error, exc);
	ret = NULL;
    } else {
	Py_INCREF(Py_None);
	ret = Py_None;
    }
    Py_DECREF(closure.error_list);
    Py_DECREF(closure.error_string);

    return ret;
}

PyDoc_STRVAR(doc_pypo_file_domain_header,
"F.domain_header([domain]) -> s.  Get the PoFile header for the\n"
"specified domain");

static PyObject *
pypo_file_domain_header(PyPoFile *self, PyObject *args)
{
    const char *domain = NULL;
    const char *header;

    if (!PyArg_ParseTuple(args, "|z:domain_header", &domain))
	return NULL;

    header = po_file_domain_header(self->pofile, domain);
    if (header) {
	    return PyBytes_FromString(header);
    }

	Py_RETURN_NONE;
}

static PyMethodDef pypo_file_methods[] = {
    { "write", (PyCFunction)pypo_file_write, METH_VARARGS,
      doc_pypo_file_write },
    { "domain_header", (PyCFunction)pypo_file_domain_header, METH_VARARGS,
      doc_pypo_file_domain_header },
    { NULL, 0, 0 }
};

PyDoc_STRVAR(doc_pypo_file_domains,
"F.domains -> list of F's domains");

static PyObject *
pypo_file_domains(PyPoFile *self, void *closure)
{
    const char * const * domains;
    PyObject *ret;

    ret = PyList_New(0);
    domains = po_file_domains(self->pofile);
    while (domains && *domains) {
	    PyObject *item = PyBytes_FromString(*domains);

	    PyList_Append(ret, item);
	    Py_DECREF(item);
	    domains++;
    }
    return ret;
}

static PyGetSetDef pypo_file_getsets[] = {
    { "domains", (getter)pypo_file_domains, (setter)0,
      doc_pypo_file_domains },
    { NULL, (getter)0, (setter)0 }
};

PyDoc_STRVAR(doc_PyPoFile_Type,
"PoFile() -> new empty PoFile instance\n"
"PoFile(filename) -> new PoFile instance containing messages from\n"
"filename");

static PyTypeObject PyPoFile_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "gettextpo.PoFile",                 /* tp_name */
    sizeof(PyPoFile),                   /* tp_basicsize */
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = doc_PyPoFile_Type,
    .tp_dealloc = (destructor)pypo_file_dealloc,
    .tp_init = (initproc)pypo_file_init,
    .tp_methods = pypo_file_methods,
    .tp_getset = pypo_file_getsets,
    .tp_iter = (getiterfunc)py_po_file_iter,
};

/* ---------------------------- */

static void
pypo_message_iterator_dealloc(PyPoMessageIterator *self)
{
    if (self->iter) {
	    po_message_iterator_free(self->iter);
        self->iter = NULL;
    }

    if (self->pofile) {
	    Py_DECREF(self->pofile);
    }
    self->pofile = NULL;

    PyObject_Del(self);
}

static PyObject *
pypo_message_iterator_iter(PyPoMessageIterator *self)
{
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *
pypo_message_iterator_next(PyPoMessageIterator *self)
{
    po_message_t msg;
    PyPoMessage *item;

    msg = po_next_message(self->iter);
    if (!msg) {
	    PyErr_SetNone(PyExc_StopIteration);
	    return NULL;
    }

    item = PyObject_New(PyPoMessage, &PyPoMessage_Type);
    if (!item) return NULL;

    item->msg = msg;
    Py_INCREF(self);
    item->pofile = (PyObject *)self;

    return (PyObject *)item;
}

PyDoc_STRVAR(doc_pypo_message_iterator_insert,
"I.insert(message) -> None.  Insert message into PoFile at this point.");

static PyObject *
pypo_message_iterator_insert(PyPoMessageIterator *self, PyObject *args)
{
    PyPoMessage *msg;

    if (!PyArg_ParseTuple(args, "O!:insert", &PyPoMessage_Type, &msg)) {
    	return NULL;
    }

    if (msg->pofile != NULL) {
	    PyErr_SetString(
            PyExc_ValueError,
			"message already a member of a PO file"
        );
	    return NULL;
    }

    po_message_insert(self->iter, msg->msg);
    Py_INCREF(self->pofile);
    msg->pofile = self->pofile;

    Py_RETURN_NONE;
}

static PyMethodDef pypo_message_iterator_methods[] = {
    { "insert", (PyCFunction)pypo_message_iterator_insert, METH_VARARGS,
      doc_pypo_message_iterator_insert },
    { NULL, 0, 0 }
};

PyDoc_STRVAR(doc_PyPoMessageIterator_Type,
"Iterator type for PoFile.  Iterates over the PoFile's messages.");

static PyTypeObject PyPoMessageIterator_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "gettextpo.PoMessageIterator",
    sizeof(PyPoMessageIterator),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = doc_PyPoMessageIterator_Type,
    .tp_dealloc = (destructor)pypo_message_iterator_dealloc,
    .tp_iter = (getiterfunc)pypo_message_iterator_iter,
    .tp_iternext = (iternextfunc)pypo_message_iterator_next,
    .tp_methods = pypo_message_iterator_methods,
};

/* ---------------------------- */

static int
pypo_message_init(PyPoMessage *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, ":__init__", kwlist)) {
	    return -1;
    }

    self->msg = po_message_create();
    if (self->msg == NULL) {
	    PyErr_SetString(PyExc_RuntimeError,
			"could not create PoMessage object");
	    return -1;
    }

    return 0;
}

static void
pypo_message_dealloc(PyPoMessage *self)
{
    po_file_t pofile;
    po_message_iterator_t iter;

    if (self->pofile) {
	    Py_DECREF(self->pofile);
    } else if (self->msg) {
        /* this pomessage has no owner, so add it to a temporary pofile */
        pofile = po_file_create();
        iter = po_message_iterator(pofile, NULL);
        po_message_insert(iter, self->msg);
        po_message_iterator_free(iter);
        po_file_free(pofile);
    }
    self->msg = NULL;
    self->pofile = NULL;

    PyObject_Del(self);
}

static PyObject *
pypo_message_repr(PyPoMessage *self)
{
    const char *msgid = NULL;

    if (self->msg)
	msgid = po_message_msgid(self->msg);

    return PyUnicode_FromFormat("<PoMessage for '%s'>",
				     msgid ? msgid : "(null)");
}

static PyObject *
pypo_message_richcmp (PyPoMessage *self, PyPoMessage *other, int op)
{
    PyObject *res;

    /* only support equality checks between PoMessage objects */
    if (!PyObject_TypeCheck(other, &PyPoMessage_Type))
	res = Py_NotImplemented;
    else if (op == Py_EQ)
	res = (self->msg == other->msg) ? Py_True : Py_False;
    else if (op == Py_NE)
	res = (self->msg != other->msg) ? Py_True : Py_False;
    else
	res = Py_NotImplemented;

    Py_INCREF(res);
    return res;
}

typedef void (po_value_setter_t)(po_message_t, const char *);

static PyObject *
_message_set_field(PyPoMessage *self, PyObject *args, const char *field,
                         po_value_setter_t * setter)
{
    const char *value;
    PyObject *object;
    PyObject *string;

    if (!PyArg_ParseTuple(args, field, &object))
        return NULL;

    if (object == Py_None) {
        (*setter)(self->msg, "");
    } else {
        string = get_pybytes_from_pyobject(object);

        if (string == NULL)
            /* Got an exception */
            return NULL;
        else {
            value = PyBytes_AsString(string);
            (*setter)(self->msg, value);
            Py_DECREF(string);
        }
    }

    Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_pypo_message_set_msgctxt,
"M.set_msgctxt(msgctxt) -> None.  Set the msgctxt for this PoMessage");

static PyObject *
pypo_message_set_msgctxt(PyPoMessage *self, PyObject *args)
{
    return _message_set_field(self, args, "O:set_msgctxt",
                                    &po_message_set_msgctxt);
}

PyDoc_STRVAR(doc_pypo_message_set_msgid,
"M.set_msgid(msgid) -> None.  Set the msgid for this PoMessage");

static PyObject *
pypo_message_set_msgid(PyPoMessage *self, PyObject *args)
{
    return _message_set_field(self, args, "O:set_msgid",
                                    &po_message_set_msgid);
}

PyDoc_STRVAR(doc_pypo_message_set_msgid_plural,
"M.set_msgid_plural(msgid_plural) -> None.  Set the plural form\n"
"msgid for this PoMessage");

static PyObject *
pypo_message_set_msgid_plural(PyPoMessage *self, PyObject *args)
{
    return _message_set_field(self, args, "O:set_msgid_plural",
                                    &po_message_set_msgid_plural);
}

PyDoc_STRVAR(doc_pypo_message_set_msgstr,
"M.set_msgstr(msgstr) -> None.  Set the msgstr for this PoMessage");

static PyObject *
pypo_message_set_msgstr(PyPoMessage *self, PyObject *args)
{
    return _message_set_field(self, args, "O:set_msgstr",
                                    &po_message_set_msgstr);
}

PyDoc_STRVAR(doc_pypo_message_set_msgstr_plural,
"M.set_msgstr_plural(index, msgstr_plural) -> None.  Set a plural\n"
"form msgstr for this PoMessage for the given index.\n"
"\n"
"A PoMessage can not have plural form msgstrs if it has no plural\n"
"form msgid");

static PyObject *
pypo_message_set_msgstr_plural(PyPoMessage *self, PyObject *args)
{
    int index;
    const char *msgstr;
    PyObject *object;
    PyObject *string;

    if (!PyArg_ParseTuple(args, "iO:set_msgstr_plural", &index, &object))
        return NULL;

    if (po_message_msgid_plural(self->msg) == NULL) {
        PyErr_SetString(PyExc_ValueError, "can not set plural msgstr with no plural msgid");
        return NULL;
    }

    if (object == Py_None) {
        po_message_set_msgstr_plural(self->msg, index, "");
    } else {
        string = get_pybytes_from_pyobject(object);

        if (string == NULL)
            /* Got an exception */
            return NULL;
        else {
            msgstr = PyBytes_AsString(string);
            po_message_set_msgstr_plural(self->msg, index, msgstr);
            Py_DECREF(string);
        }
    }

    Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_pypo_message_set_comments,
"M.set_comments(comments) -> None.  Set the comments for the\n"
"PoMessage.");

static PyObject *
pypo_message_set_comments(PyPoMessage *self, PyObject *args)
{
    return _message_set_field(self, args, "O:set_comments",
                                    &po_message_set_comments);
}

PyDoc_STRVAR(doc_pypo_message_set_format,
"M.set_format(format_type, boolean) -> None.  Set or unset the \n"
"given format flag.\n"
"\n"
"Possible format types include 'c-format', 'python-format', etc.");

static PyObject *
pypo_message_set_format(PyPoMessage *self, PyObject *args)
{
    const char *format_type;
    int value;

    if (!PyArg_ParseTuple(args, "zi:set_format", &format_type, &value))
	return NULL;

    po_message_set_format(self->msg, format_type, value);

    Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_pypo_message_check_format,
"M.check_format() -> None.  Check that format strings are\n"
"translated correctly.\n"
"\n"
"This function will be a no-op if no format type is set for the\n"
"message.  If the format string is not translated correctly, the\n"
"gettextpo.error exception is raised.");

/* This function depends on the Python Global Interpreter Lock for
 * synchronising access to the "error_closure" global variable. */
static PyObject *
pypo_message_check_format(PyPoMessage *self)
{
    ErrorClosure closure;
    PyObject *ret;

    /* gettext-0.15 no longer includes NULL checks for msgstr, while
     * old versions did.  We do the check here and exit early to
     * provide the same behaviour as old versions.
     */
    if (po_message_msgid(self->msg) == NULL ||
	strlen(po_message_msgid(self->msg)) == 0 ||
	po_message_msgstr(self->msg) == NULL ||
	strlen(po_message_msgstr(self->msg)) == 0) {
	Py_RETURN_NONE;
    }

    closure.error_list = PyList_New(0);
    closure.error_string = PyUnicode_FromString("");

    PyThread_acquire_lock(error_closure_lock, WAIT_LOCK);
    error_closure = &closure;

    if (setjmp(closure.env) == 0) {
	po_message_check_format(self->msg, &error_handler);
    }

    error_closure = NULL;
    PyThread_release_lock(error_closure_lock);

    if (PyUnicode_GetLength(closure.error_string) != 0) {
	PyObject *exc;

	/* set up the exception */
	exc = PyObject_CallFunction(gettextpo_error,
				    "O", closure.error_string);
	PyObject_SetAttrString(exc, "error_list", closure.error_list);

	PyErr_SetObject(gettextpo_error, exc);
	ret = NULL;
    } else {
	Py_INCREF(Py_None);
	ret = Py_None;
    }
    Py_DECREF(closure.error_list);
    Py_DECREF(closure.error_string);

    return ret;
}

static PyMethodDef pypo_message_methods[] = {
    { "set_msgctxt", (PyCFunction)pypo_message_set_msgctxt, METH_VARARGS,
      doc_pypo_message_set_msgctxt },
    { "set_msgid", (PyCFunction)pypo_message_set_msgid, METH_VARARGS,
      doc_pypo_message_set_msgid },
    { "set_msgid_plural", (PyCFunction)pypo_message_set_msgid_plural, METH_VARARGS,
      doc_pypo_message_set_msgid_plural },
    { "set_msgstr", (PyCFunction)pypo_message_set_msgstr, METH_VARARGS,
      doc_pypo_message_set_msgstr },
    { "set_msgstr_plural", (PyCFunction)pypo_message_set_msgstr_plural, METH_VARARGS,
      doc_pypo_message_set_msgstr_plural },
    { "set_comments", (PyCFunction)pypo_message_set_comments, METH_VARARGS,
      doc_pypo_message_set_comments },
    { "set_format", (PyCFunction)pypo_message_set_format, METH_VARARGS,
      doc_pypo_message_set_format },
    { "check_format", (PyCFunction)pypo_message_check_format, METH_NOARGS,
      doc_pypo_message_check_format },
    { NULL, 0, 0 }
};

PyDoc_STRVAR(doc_pypo_message_msgctxt,
"M.msgctxt -> the msgctxt for this PoMessage.");

static PyObject *
pypo_message_get_msgctxt(PyPoMessage *self, void *closure)
{
    const char *msgctxt;

    msgctxt = po_message_msgctxt(self->msg);
    if (msgctxt)
	return PyBytes_FromString(msgctxt);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_pypo_message_msgid,
"M.msgid -> the msgid for this PoMessage.");

static PyObject *
pypo_message_get_msgid(PyPoMessage *self, void *closure)
{
    const char *msgid;

    msgid = po_message_msgid(self->msg);
    if (!msgid || msgid[0] == '\0') {
        Py_RETURN_NONE;
    }
    return PyBytes_FromString(msgid);
}

PyDoc_STRVAR(doc_pypo_message_msgid_plural,
"M.msgid_plural -> the plural form msgid for this PoMessage.");

static PyObject *
pypo_message_get_msgid_plural(PyPoMessage *self, void *closure)
{
    const char *msgid_plural;

    msgid_plural = po_message_msgid_plural(self->msg);
    if (msgid_plural)
	return PyBytes_FromString(msgid_plural);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_pypo_message_msgstr,
"M.msgid -> the translated msgstr for this PoMessage.");

static PyObject *
pypo_message_get_msgstr(PyPoMessage *self, void *closure)
{
    const char *msgstr;
    PyObject *ret;

    msgstr = po_message_msgstr(self->msg);
    if (msgstr[0] != '\0') {  // if the string is not empty
        ret = PyBytes_FromString(msgstr);
        if (ret) {
            return ret;
        } else {
            Py_DECREF(ret);
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(doc_pypo_message_msgstr_plural,
"M.msgid_plural -> list of plural form msgstr for this PoMessage.");

static PyObject *
pypo_message_get_msgstr_plural(PyPoMessage *self, void *closure)
{
    const char *msgstr;
    int i;
    PyObject *ret, *item;

    ret = PyList_New(0);
    i = 0;
    msgstr = po_message_msgstr_plural(self->msg, i);
    while (msgstr) {
	item = PyBytes_FromString(msgstr);
	PyList_Append(ret, item);
	Py_DECREF(item);

	i++;
	msgstr = po_message_msgstr_plural(self->msg, i);
    }
    return ret;
}

PyDoc_STRVAR(doc_pypo_message_comments,
"M.comments -> comments associated with this PoMessage.");

static PyObject *
pypo_message_get_comments(PyPoMessage *self, void *closure)
{
    const char *comments;

    comments = po_message_comments(self->msg);
    if (comments)
	return PyBytes_FromString(comments);
    Py_RETURN_NONE;
}


static PyGetSetDef pypo_message_getsets[] = {
    { "msgctxt", (getter)pypo_message_get_msgctxt,             (setter)0,
      doc_pypo_message_msgctxt },
    { "msgid", (getter)pypo_message_get_msgid,                 (setter)0,
      doc_pypo_message_msgid },
    { "msgid_plural", (getter)pypo_message_get_msgid_plural,   (setter)0,
      doc_pypo_message_msgid_plural },
    { "msgstr", (getter)pypo_message_get_msgstr,               (setter)0,
      doc_pypo_message_msgstr },
    { "msgstr_plural", (getter)pypo_message_get_msgstr_plural, (setter)0,
      doc_pypo_message_msgstr_plural },
    { "comments", (getter)pypo_message_get_comments,           (setter)0,
      doc_pypo_message_comments },
    { NULL, (getter)0, (setter)0 }
};

PyDoc_STRVAR(doc_PyPoMessage_Type,
"PyMessage() -> new empty PoMessage instance.");

static PyTypeObject PyPoMessage_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "gettextpo.PoMessage",              /* tp_name */
    sizeof(PyPoMessage),                /* tp_basicsize */
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = doc_PyPoMessage_Type,
    .tp_dealloc = (destructor)pypo_message_dealloc,
    .tp_init = (initproc)pypo_message_init,
    .tp_repr = (reprfunc)pypo_message_repr,
    .tp_richcompare = (richcmpfunc)pypo_message_richcmp,
    .tp_methods = pypo_message_methods,
    .tp_getset = pypo_message_getsets,
};

PyDoc_STRVAR(doc_gettextpo,
"PO file parsing and writing support.\n"
"\n"
"This module wraps GNU gettext's PO file parser and writer.  This could\n"
"be of use to translation applications, or applications that need to\n"
"manipulate or validate translations.");

#define MOD_DEF(ob, name, doc, methods) \
do { \
    static struct PyModuleDef moduledef = { \
        PyModuleDef_HEAD_INIT, name, doc, -1, methods \
    }; \
    ob = PyModule_Create(&moduledef); \
} while (0);


static PyObject *
do_init(void)
{
    PyObject *mod;

    if (libgettextpo_version < MIN_REQUIRED_GETTEXTPO_VERSION) {
	    PyErr_SetString(PyExc_RuntimeError, "version of libgettextpo too old");
	    return NULL;
    }

    gettextpo_error = PyErr_NewException("gettextpo.error",
					 PyExc_RuntimeError, NULL);

    error_closure_lock = PyThread_allocate_lock();

    /* initialise PoMessage type */
#define INIT_TYPE(type)                      \
    if (!type.tp_alloc)                      \
	type.tp_alloc = PyType_GenericAlloc; \
    if (!type.tp_new)                        \
	type.tp_new = PyType_GenericNew;     \
    if (PyType_Ready(&type) < 0)             \
	return NULL

    INIT_TYPE(PyPoFile_Type);
    INIT_TYPE(PyPoMessageIterator_Type);
    INIT_TYPE(PyPoMessage_Type);

    MOD_DEF(mod, "gettextpo", doc_gettextpo, NULL);

    Py_INCREF(&PyPoFile_Type);
    PyModule_AddObject(mod, "PoFile", (PyObject *)&PyPoFile_Type);
    Py_INCREF(&PyPoMessage_Type);
    PyModule_AddObject(mod, "PoMessage", (PyObject *)&PyPoMessage_Type);
    Py_INCREF(gettextpo_error);
    PyModule_AddObject(mod, "error", gettextpo_error);

    return mod;
}

PyMODINIT_FUNC PyInit_gettextpo(void) {
    return do_init();
}
