import axios from '../lib/axios'

export default function CrudManager({ url, showLoader, hideLoader, showError, hideError }) {

    const api = "api/"

    // Ver los datos 
    const views = async ({ setData, setLoading, setErrors, setPages }) => {
        setLoading(true);
        await axios
            .get(api + url)
            .then(res => {
                setData(res.data.data ?? res.data);
                if (typeof setPages === 'function') {
                    setPages(res?.data?.data?.last_page ?? res?.data?.last_page);
                }
            })
            .catch(error => {
                if (error.response && error.response.data.errors) {
                    setErrors(Object.values(error.response.data.errors).flat());
                }
                throw error;
            })
            .finally(() => { setLoading(false); });
    };

    // Crear los datos
    const creates = async ({ setErrors, setStatus, ...props }) => {
        setErrors(null);
        setStatus(true);
        return await axios
            .post(api + url, props.data)
            .then((res) => {
                setStatus("success");
                showLoader();
                setTimeout(() => hideLoader(), 4000);
                return res.data;
            })
            .catch((error) => {
                if (error.response && error.response.data.errors) {
                    setErrors(Object.values(error.response.data.errors).flat());
                }
                setStatus(false);
                showError();
                setTimeout(() => hideError(), 4000);
                setErrors(error)
                throw error;
            });
    };

    // Actualizar los datos
    const updates = async ({ setErrors, setStatus, ...props }) => {
        setErrors(null);
        setStatus(true);

        const endpoint = props.id ? `${api}${url}/${props.id}` : `${api}${url}`;

        return axios
            .put(endpoint, props.data)
            .then(res => {
                showLoader();
                setTimeout(() => hideLoader(), 4000);
                return res.data
            })
            .catch(error => {
                if (error.response && error.response.data.errors) {
                    setErrors(Object.values(error.response.data.errors).flat());
                }
                setStatus(false);
                showError();
                setTimeout(() => hideError(), 4000);
                setErrors(error);
                throw error;
            });
    };

    // Borrar los datos
    const deletes = async ({ setErrors, setStatus, ElementId }) => {
        setErrors(null);
        setStatus(true);
        await axios
            .delete(`${api}${url}/${ElementId}`,)
            .then(res => {
                showLoader();
                setTimeout(() => hideLoader(), 4000);
                res.data
            })
            .catch(error => {
                setStatus(false);
                setErrors(error.response.data.errors);
                showError();
                setTimeout(() => hideError(), 4000);
            });
    };

    return {
        views,
        creates,
        updates,
        deletes
    };

}; 