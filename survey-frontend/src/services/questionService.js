import api from "@/constants/api"

export const questionService = {
    getQuestions(page, size) {
        return api.get(`/api/v1/questions/?page=${page}&page_size=${size}`)
    },

    getQuestionTypes() {
        return api.get('/api/v1/question_types/')
    },

    createQuestion(data) {
        return api.post('/api/v1/questions/', data)
    },

    deleteQuestion(id) {
        return api.delete(`/api/v1/questions/${id}`)
    },

    getQuestionDetail(id) {
        return api.get(`/api/v1/questions/${id}`)
    },

    // updateQuestion(id, data) {
    //     return api.put(`/api/v1/questions/${id}/`, data)
    // },

    updateQuestion(id, data) {
        return api.patch(`/api/v1/questions/${id}/`, data)
    },

    deleteQuestionOption(question_id, option_id) {
        return api.delete(`/api/v1/questions/${question_id}/options/${option_id}/`)
    },

    getQuestionOptions(id) {
        return api.get(`/api/v1/questions/${id}/options/`)
    },

    updateQuestionOption(question_id, option_id, data) {
        return api.put(`/api/v1/questions/${question_id}/options/${option_id}/`, data)
    },

    createQuestionOption(question_id, data) {
        return api.post(`/api/v1/questions/${question_id}/options/`, data)
    },

    addQuestionToSet(survey_id, set_id, data){
        return api.post(`/api/v1/surveys/${survey_id}/sets/${set_id}/questions/`, data)
    },

    removeQuestionFromSet(survey_id, set_id, question_id){
        return api.delete(`/api/v1/surveys/${survey_id}/sets/${set_id}/questions/${question_id}/`)
    }
}
