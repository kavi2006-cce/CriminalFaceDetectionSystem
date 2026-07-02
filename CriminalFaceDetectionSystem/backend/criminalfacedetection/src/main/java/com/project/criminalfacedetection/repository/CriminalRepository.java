package com.project.criminalfacedetection.repository;

import com.project.criminalfacedetection.model.Criminal;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CriminalRepository extends JpaRepository<Criminal, Long> {
}